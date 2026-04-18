"""
Shared sensor ingestion route.
POST /api/sensors/data  — called by ESP32 firmware every CLOUD_SEND_INTERVAL_MS
Automatically evaluates irrigation status and writes alerts when needed.
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from database import get_db
from models.sensor_data import SensorReading, Alert
from controllers.irrigation_controller import IrrigationController

router = APIRouter()


# ── POST /api/sensors/data ─────────────────────────────────────────────────
@router.post("/data", status_code=201)
async def ingest_sensor_data(reading: SensorReading):
    """
    Called by the ESP32 every CLOUD_SEND_INTERVAL_MS.
    Stores the reading and triggers server-side irrigation evaluation.
    Writes an alert document if severity is critical or warning.
    """
    db  = get_db()
    doc = reading.model_dump()
    doc["created_at"] = datetime.now(timezone.utc)

    result = await db.sensor_readings.insert_one(doc)
    doc["_id"] = result.inserted_id  # needed for evaluate_status timestamp

    # Evaluate and optionally alert
    status = IrrigationController.evaluate_status(doc)
    if status["severity"] != "normal":
        alert = Alert(
            component="irrigation",
            severity=status["severity"],
            message=status["message"],
        )
        await db.alerts.insert_one(alert.model_dump())

    return {
        "inserted_id":       str(result.inserted_id),
        "status":            "stored",
        "irrigation_status": status["status"],
    }


# ── GET /api/sensors/latest ────────────────────────────────────────────────
@router.get("/latest")
async def get_latest_reading():
    """Returns the most recent sensor snapshot — used by the dashboard."""
    db  = get_db()
    doc = await db.sensor_readings.find_one(sort=[("created_at", -1)])
    if not doc:
        raise HTTPException(status_code=404, detail="No sensor data found yet.")
    doc["_id"] = str(doc["_id"])
    return doc


# ── GET /api/sensors/history?limit=50 ─────────────────────────────────────
@router.get("/history")
async def get_sensor_history(limit: int = 50):
    """Returns last N readings in reverse-chronological order."""
    db     = get_db()
    cursor = db.sensor_readings.find(sort=[("created_at", -1)], limit=limit)
    docs   = await cursor.to_list(length=limit)
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs


# ── GET /api/sensors/alerts ────────────────────────────────────────────────
@router.get("/alerts")
async def get_all_alerts(resolved: bool = False, limit: int = 50):
    """Returns unresolved (or resolved) alerts, most-recent first."""
    db     = get_db()
    cursor = db.alerts.find(
        {"resolved": resolved},
        sort=[("timestamp", -1)],
        limit=limit,
    )
    docs = await cursor.to_list(length=limit)
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs