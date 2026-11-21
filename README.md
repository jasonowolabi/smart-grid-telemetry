# Smart Grid Telemetry System

A real-time smart grid telemetry simulation and monitoring dashboard built with Python, FastAPI, Pydantic, Uvicorn, an asynchronous background worker (`asyncio.Queue`), and a Tailwind CSS frontend. The system simulates telemetry streams from substation meters across Lagos zones—including Ikeja, Lekki, Yaba, Victoria Island, Surulere, and Oshodi—while evaluating power consumption, blackouts, and voltage surges in real time.

## Architecture Overview

The application decouples high-throughput telemetry ingestion from state evaluation and dashboard reads using an in-memory asynchronous queue:

1. **Simulator (`simulator.py`)**: Generates periodic telemetry payloads (`meter_id`, `zone`, `voltage`, `current`) for simulated Lagos meter nodes, including normal operating voltages as well as outage and surge scenarios, and posts them to the ingestion API.
2. **Ingestion API (`app/main.py`)**: Exposes `POST /api/v1/telemetry`, validates incoming payloads via Pydantic (`TelemetryPayload`), enqueues items onto `asyncio.Queue` without blocking, and returns `202 Accepted`.
3. **Background Worker (`worker/processor.py`)**: Started on application startup (`@app.on_event("startup")`), consumes queued payloads asynchronously, computes `kwh_consumed`, classifies meter health (`ACTIVE`, `OUTAGE`, or `SURGE`), updates in-memory state (`live_meters`), and records state-transition alerts (`alert_history`).
4. **State & Dashboard (`app/main.py`, `app/static/index.html`)**: Exposes `GET /api/v1/grid/state` for live polling and serves a responsive Tailwind CSS operations dashboard displaying summary metrics, individual substation meter cards, and an incident alert stream.

## Threshold and Anomaly Rules

Meter status is evaluated from incoming voltage (`voltage`):

- **OUTAGE**: `voltage == 0`
- **SURGE**: `voltage > 250.0` or `voltage < 190.0`
- **ACTIVE**: All other valid voltages within `[190.0, 250.0]`

## Project Structure

```text
smart-grid-telemetry/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── static/
│       └── index.html
├── worker/
│   ├── __init__.py
│   ├── models.py
│   └── processor.py
├── simulator.py
├── requirements.txt
├── .gitignore
└── README.md
