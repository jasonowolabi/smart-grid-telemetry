import asyncio
import random
import httpx

API_URL = "http://127.0.0.1:8000/api/v1/telemetry"

METERS = [
    {"meter_id": "MTR-IKEJA-01", "zone": "Ikeja"},
    {"meter_id": "MTR-IKEJA-02", "zone": "Ikeja"},
    {"meter_id": "MTR-LEKKI-01", "zone": "Lekki"},
    {"meter_id": "MTR-LEKKI-02", "zone": "Lekki"},
    {"meter_id": "MTR-YABA-01", "zone": "Yaba"},
    {"meter_id": "MTR-YABA-02", "zone": "Yaba"},
    {"meter_id": "MTR-VI-01", "zone": "Victoria Island"},
    {"meter_id": "MTR-SURULERE-01", "zone": "Surulere"},
    {"meter_id": "MTR-SURULERE-02", "zone": "Surulere"},
    {"meter_id": "MTR-OSHODI-01", "zone": "Oshodi"},
]

async def simulate_meter(client: httpx.AsyncClient, meter: dict):
    while True:
        try:
            roll = random.random()
            if roll < 0.85:
                voltage = round(random.uniform(215.0, 240.0), 1)
                current = round(random.uniform(5.0, 18.0), 1)
            elif roll < 0.95:
                voltage = 0.0
                current = 0.0
            else:
                voltage = round(random.uniform(255.0, 275.0), 1)
                current = round(random.uniform(20.0, 25.0), 1)

            payload = {
                "meter_id": meter["meter_id"],
                "zone": meter["zone"],
                "voltage": voltage,
                "current": current
            }

            response = await client.post(API_URL, json=payload, timeout=2.0)
            if response.status_code == 202:
                print(f"[SENT] {meter['meter_id']} ({meter['zone']}) -> {voltage}V")
            else:
                print(f"[ERROR {response.status_code}] {meter['meter_id']} -> {response.text}")

        except httpx.RequestError:
            print(f"[WARNING] Could not connect to API server.")

        await asyncio.sleep(1.5)

async def main():
    print("⚡ Starting Lagos Smart Meter Simulator...")
    async with httpx.AsyncClient() as client:
        tasks = [simulate_meter(client, meter) for meter in METERS]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Simulator stopped.")