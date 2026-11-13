import asyncio
from datetime import datetime, timezone
from typing import Dict, List
from worker.models import Payload, MeterStatus

# Asynchronous queue acting as our message broker
telemetry_queue: asyncio.Queue[Payload] = asyncio.Queue()

# In-memory state store for live dashboard reads
live_meters: Dict[str, MeterStatus] = {}

# Recent anomaly alerts log
alert_history: List[dict] = []


def evaluate_meter_status(voltage: float) -> str:
    """Determine grid node state based on incoming voltage."""
    if voltage == 0:
        return "OUTAGE"
    elif voltage > 250.0 or voltage < 190.0:
        return "SURGE"
    return "ACTIVE"


async def process_telemetry_stream():
    """Background worker loop that consumes queued telemetry payloads."""
    print("⚙️ [WORKER] Background telemetry processor loop started and waiting for items...")
    while True:
        try:
            # Wait for data to arrive in the queue
            payload: Payload = await telemetry_queue.get()
            print(f"📥 [WORKER] Pulled item from queue: {payload.meter_id} ({payload.voltage}V)")

            now_str = datetime.now(timezone.utc).strftime("%H:%M:%S")
            kwh_consumed = round((payload.voltage * payload.current) / 1000.0, 3)
            status = evaluate_meter_status(payload.voltage)

            previous = live_meters.get(payload.meter_id)

            # Update latest state in memory
            live_meters[payload.meter_id] = MeterStatus(
                meter_id=payload.meter_id,
                zone=payload.zone,
                voltage=payload.voltage,
                current=payload.current,
                kwh_consumed=kwh_consumed,
                status=status,
                last_updated=now_str,
            )

            print(f"📊 [WORKER] Updated live state for {payload.meter_id}. Total active meters in memory: {len(live_meters)}")

            # Log an alert whenever a meter transitions into OUTAGE or SURGE
            if status in ("OUTAGE", "SURGE") and (not previous or previous.status != status):
                alert_history.insert(0, {
                    "meter_id": payload.meter_id,
                    "zone": payload.zone,
                    "status": status,
                    "voltage": payload.voltage,
                    "timestamp": now_str,
                    "message": (
                        f"Blackout detected in {payload.zone} ({payload.meter_id})"
                        if status == "OUTAGE"
                        else f"Voltage anomaly ({payload.voltage}V) in {payload.zone}"
                    ),
                })
                del alert_history[25:]

            telemetry_queue.task_done()

        except Exception as e:
            print(f"❌ [WORKER ERROR] {e}")