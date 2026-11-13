import asyncio
from fastapi import FastAPI, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from worker.models import Payload
from worker.processor import (
    telemetry_queue,
    live_meters,
    alert_history,
    process_telemetry_stream,
)

app = FastAPI(title="Smart Grid Telemetry Simulation")

# Mount static directory for our visual dashboard
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
async def startup_event():
    """Guaranteed background worker startup across all FastAPI versions."""
    asyncio.create_task(process_telemetry_stream())
    print("🚀 Background telemetry worker task created successfully!")


@app.get("/")
async def serve_dashboard():
    """Serve the interactive visual grid simulation."""
    return FileResponse("app/static/index.html")


@app.post("/api/v1/telemetry", status_code=status.HTTP_202_ACCEPTED)
async def ingest_telemetry(payload: Payload):
    """Non-blocking ingestion endpoint: pushes payload to queue and returns 202."""
    await telemetry_queue.put(payload)
    return {
        "status": "QUEUED",
        "meter_id": payload.meter_id,
        "queue_depth": telemetry_queue.qsize(),
    }


@app.get("/api/v1/grid/state")
async def get_grid_state():
    """Endpoint polled by the visual dashboard for live meter states & alerts."""
    meters_list = list(live_meters.values())
    active_count = sum(1 for m in meters_list if m.status == "ACTIVE")
    outage_count = sum(1 for m in meters_list if m.status == "OUTAGE")
    surge_count = sum(1 for m in meters_list if m.status == "SURGE")
    total_kw = round(sum(m.kwh_consumed for m in meters_list), 2)

    return {
        "summary": {
            "total_meters": len(meters_list),
            "active": active_count,
            "outages": outage_count,
            "surges": surge_count,
            "total_kw": total_kw,
            "queue_depth": telemetry_queue.qsize(),
        },
        "meters": meters_list,
        "alerts": alert_history,
    }