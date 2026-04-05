"""
COMPONENT 3 — Soil pH Monitoring
Owner: Ravisha
Routes: /api/ph/...
"""
from fastapi import APIRouter, HTTPException
from database import get_db
from controllers.ph_controller import PHController

router = APIRouter()

@router.get("/status")
async def get_ph_status():
    """Returns current pH, status label, and immediate advice."""
    db = get_db()
    doc = await db.sensor_readings.find_one(sort=[("created_at", -1)])
    if not doc:
        raise HTTPException(status_code=404, detail="No sensor data available.")
    return PHController.evaluate_status(doc)

@router.get("/correction")
async def get_ph_correction():
    """
    ML regression model — recommends lime/sulphur quantity
    based on current pH and crop stage.
    """
    db = get_db()
    cursor = db.sensor_readings.find(sort=[("created_at", -1)], limit=10)
    history = await cursor.to_list(length=10)
    if not history:
        raise HTTPException(status_code=404, detail="No sensor data available.")
    return await PHController.correction_plan(history)

@router.get("/history")
async def get_ph_history(limit: int = 30):
    """Returns pH history for trend chart."""
    db = get_db()
    cursor = db.sensor_readings.find(
        {}, {"ph": 1, "created_at": 1},
        sort=[("created_at", -1)], limit=limit
    )
    docs = await cursor.to_list(length=limit)
    for d in docs:
        d["_id"] = str(d["_id"])
    return list(reversed(docs))
