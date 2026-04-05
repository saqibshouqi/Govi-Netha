"""
COMPONENT 4 — Crop Stress Detection
Owner: Roshana
Routes: /api/stress/...
"""
from fastapi import APIRouter, HTTPException
from database import get_db
from controllers.stress_controller import StressController

router = APIRouter()

@router.get("/level")
async def get_stress_level():
    """
    Returns current stress index (0–100) and contributing factors.
    """
    db = get_db()
    doc = await db.sensor_readings.find_one(sort=[("created_at", -1)])
    if not doc:
        raise HTTPException(status_code=404, detail="No sensor data available.")
    return StressController.evaluate_stress(doc)

@router.get("/prediction")
async def get_stress_prediction():
    """
    ML classification — predicts yield reduction risk from environmental trends.
    """
    db = get_db()
    cursor = db.sensor_readings.find(sort=[("created_at", -1)], limit=20)
    history = await cursor.to_list(length=20)
    if len(history) < 3:
        raise HTTPException(status_code=400,
                            detail="Need at least 3 readings for stress prediction.")
    return await StressController.predict_risk(history)

@router.get("/history")
async def get_stress_history(limit: int = 30):
    """Returns temperature + humidity history for charts."""
    db = get_db()
    cursor = db.sensor_readings.find(
        {}, {"temperature": 1, "humidity": 1, "moisture": 1, "created_at": 1},
        sort=[("created_at", -1)], limit=limit
    )
    docs = await cursor.to_list(length=limit)
    for d in docs:
        d["_id"] = str(d["_id"])
    return list(reversed(docs))
