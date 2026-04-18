"""
Sensor data models — irrigation scope only.
Matches the payload sent by the ESP32 firmware (main.cpp → sendToCloud).
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SensorReading(BaseModel):
    """Payload the ESP32 POSTs to /api/sensors/data"""
    moisture:    float = Field(..., ge=0, le=100,  description="Soil moisture %")
    temperature: float = Field(..., ge=-10, le=60, description="Air temperature °C")
    humidity:    float = Field(..., ge=0, le=100,  description="Relative humidity %")
    # Set by TFLite edge classifier on the ESP32
    edge_state:  Optional[int] = Field(None, description="0=OK, 1=IRRIGATE_SOON, 2=IRRIGATE_NOW")
    edge_label:  Optional[str] = Field(None, description="Human-readable edge AI label")
    timestamp:   Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "moisture": 55.0,
                "temperature": 29.5,
                "humidity": 72.0,
                "edge_state": 0,
                "edge_label": "OK",
            }
        }


class SensorDocument(SensorReading):
    """Document as stored in MongoDB (adds server-side timestamp)."""
    id:         Optional[str]  = Field(None, alias="_id")
    created_at: datetime       = Field(default_factory=datetime.utcnow)


class Alert(BaseModel):
    """Written whenever a sensor reading triggers a non-normal status."""
    component:  str       # "irrigation"
    severity:   str       # "critical" | "warning" | "normal"
    message:    str
    timestamp:  datetime  = Field(default_factory=datetime.utcnow)
    resolved:   bool      = False