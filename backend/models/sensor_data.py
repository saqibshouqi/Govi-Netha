from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ── Incoming from ESP32 ────────────────────────────────────────
class SensorReading(BaseModel):
    """Payload the ESP32 POSTs to /api/sensors/data"""
    moisture:    float = Field(..., ge=0, le=100,  description="Soil moisture %")
    temperature: float = Field(..., ge=-10, le=60, description="Air temperature °C")
    humidity:    float = Field(..., ge=0, le=100,  description="Relative humidity %")
    ph:          float = Field(..., ge=0, le=14,   description="Soil pH")
    nitrogen:    float = Field(..., ge=0,           description="Nitrogen mg/kg")
    phosphorus:  float = Field(..., ge=0,           description="Phosphorus mg/kg")
    potassium:   float = Field(..., ge=0,           description="Potassium mg/kg")
    timestamp:   Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "moisture": 62.0, "temperature": 28.5, "humidity": 75.0,
                "ph": 6.5, "nitrogen": 78.0, "phosphorus": 45.0, "potassium": 82.0
            }
        }

# ── Stored in MongoDB (adds _id + server timestamp) ───────────
class SensorDocument(SensorReading):
    id: Optional[str] = Field(None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ── Alert model (written by any component) ────────────────────
class Alert(BaseModel):
    component:  str   # "irrigation" | "npk" | "ph" | "stress"
    severity:   str   # "critical" | "warning" | "normal"
    message:    str
    timestamp:  datetime = Field(default_factory=datetime.utcnow)
    resolved:   bool = False
