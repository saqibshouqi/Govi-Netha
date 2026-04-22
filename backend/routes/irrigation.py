"""
Smart Irrigation - Routes
Prefix: /api/irrigation
"""
from fastapi import APIRouter, HTTPException

from database import get_db
from controllers.irrigation_controller import IrrigationController

router = APIRouter()


@router.get("/status")
async def get_irrigation_status():
    """
    Returns current irrigation recommendation based on the latest sensor reading.
    Response includes: status, severity, message, moisture_pct, temperature_c.
    """
    db  = get_db()
    doc = await db.sensor_readings.find_one(sort=[("created_at", -1)])
    if not doc:
        raise HTTPException(status_code=404, detail="No sensor data available yet.")
    return IrrigationController.evaluate_status(doc)


@router.get("/prediction")
async def get_irrigation_prediction():
    """
    ML-powered prediction of hours until next irrigation is needed.
    Falls back to rule-based estimate when model.pkl is not trained yet.
    Requires at least 3 historical readings.
    """
    db     = get_db()
    cursor = db.sensor_readings.find(sort=[("created_at", -1)], limit=20)
    history = await cursor.to_list(length=20)
    if len(history) < 3:
        raise HTTPException(
            status_code=400,
            detail="Need at least 3 sensor readings for prediction. Keep the ESP32 running.",
        )
    return await IrrigationController.predict(history)


@router.get("/history")
async def get_irrigation_history(limit: int = 30):
    """
    Returns moisture + temperature readings in chronological order.
    Used by the frontend trend chart.
    """
    db     = get_db()
    cursor = db.sensor_readings.find(
        {},
        {"moisture": 1, "temperature": 1, "humidity": 1, "created_at": 1},
        sort=[("created_at", -1)],
        limit=limit,
    )
    docs = await cursor.to_list(length=limit)
    for d in docs:
        d["_id"] = str(d["_id"])
    return list(reversed(docs))  # chronological for charts