"""
COMPONENT 2 — Soil Nutrient (NPK) Deficiency Detection
Owner: Januki
Routes: /api/npk/...
"""
from fastapi import APIRouter, HTTPException
from database import get_db
from controllers.npk_controller import NPKController

router = APIRouter()

@router.get("/status")
async def get_npk_status():
    """
    Returns current NPK levels and deficiency flags.
    """
    db = get_db()
    doc = await db.sensor_readings.find_one(sort=[("created_at", -1)])
    if not doc:
        raise HTTPException(status_code=404, detail="No sensor data available.")
    return NPKController.evaluate_status(doc)

@router.get("/recommendation")
async def get_npk_recommendation():
    """
    ML classification model — recommends fertilizer type and quantity.
    """
    db = get_db()
    cursor = db.sensor_readings.find(sort=[("created_at", -1)], limit=10)
    history = await cursor.to_list(length=10)
    if not history:
        raise HTTPException(status_code=404, detail="No sensor data available.")
    return await NPKController.recommend(history)

@router.get("/history")
async def get_npk_history(limit: int = 30):
    """Returns N, P, K history for trend charts."""
    db = get_db()
    cursor = db.sensor_readings.find(
        {}, {"nitrogen": 1, "phosphorus": 1, "potassium": 1, "created_at": 1},
        sort=[("created_at", -1)], limit=limit
    )
    docs = await cursor.to_list(length=limit)
    for d in docs:
        d["_id"] = str(d["_id"])
    return list(reversed(docs))
