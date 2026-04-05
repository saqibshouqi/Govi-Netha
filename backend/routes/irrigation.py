"""
COMPONENT 1 — Smart Irrigation Optimization
Owner: Saqib
Routes: /api/irrigation/...
"""
from fastapi import APIRouter, HTTPException
from database import get_db
from controllers.irrigation_controller import IrrigationController

router = APIRouter()

@router.get("/status")
async def get_irrigation_status():
    """
    Real-time irrigation recommendation based on latest sensor reading.
    Returns: status (irrigate_now | monitor | ok), moisture %, reason
    """
    db = get_db()
    doc = await db.sensor_readings.find_one(sort=[("created_at", -1)])
    if not doc:
        raise HTTPException(status_code=404, detail="No sensor data available.")
    return IrrigationController.evaluate_status(doc)

@router.get("/prediction")
async def get_irrigation_prediction():
    """
    ML-powered prediction: next optimal irrigation window.
    Uses Random Forest trained on historical moisture + temperature trends.
    """
    db = get_db()
    # Fetch last 20 readings for trend analysis
    cursor = db.sensor_readings.find(sort=[("created_at", -1)], limit=20)
    history = await cursor.to_list(length=20)
    if len(history) < 3:
        raise HTTPException(status_code=400,
                            detail="Not enough historical data yet (need at least 3 readings).")
    return await IrrigationController.predict(history)

@router.get("/history")
async def get_irrigation_history(limit: int = 30):
    """Returns moisture + irrigation status history for charts."""
    db = get_db()
    cursor = db.sensor_readings.find(
        {}, {"moisture": 1, "temperature": 1, "created_at": 1},
        sort=[("created_at", -1)], limit=limit
    )
    docs = await cursor.to_list(length=limit)
    for d in docs:
        d["_id"] = str(d["_id"])
    return list(reversed(docs))  # chronological order for charts
