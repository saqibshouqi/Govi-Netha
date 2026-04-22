"""
COMPONENT 1 — Irrigation Controller
Owner: Saqib
Business logic: threshold evaluation + ML prediction calls
"""
import joblib
import numpy as np
from pathlib import Path
from datetime import datetime, timezone

MODEL_PATH = Path(__file__).parent.parent / "ml" / "irrigation" / "model.pkl"

# Thresholds (mirror edge/src/config.h)
MOISTURE_CRITICAL = 40.0
MOISTURE_WARNING  = 60.0
TEMP_HIGH         = 35.0

class IrrigationController:

    @staticmethod
    def evaluate_status(doc: dict) -> dict:
        moisture = doc.get("moisture", 0)
        temp     = doc.get("temperature", 0)

        if moisture < MOISTURE_CRITICAL:
            status  = "irrigate_now"
            severity = "critical"
            message = f"Soil moisture critically low ({moisture:.1f}%). Irrigate immediately."
        elif moisture < MOISTURE_WARNING and temp > TEMP_HIGH:
            status  = "irrigate_soon"
            severity = "warning"
            message = f"Moisture {moisture:.1f}% + high temp {temp:.1f}°C. Irrigate within 2 hours."
        elif moisture < MOISTURE_WARNING:
            status  = "monitor"
            severity = "warning"
            message = f"Moisture {moisture:.1f}% slightly below optimal. Monitor closely."
        else:
            status  = "ok"
            severity = "normal"
            message = f"Soil moisture {moisture:.1f}% — no irrigation needed."

        return {
            "status": status,
            "severity": severity,
            "message": message,
            "moisture_pct": moisture,
            "temperature_c": temp,
            "timestamp": doc.get("created_at"),
        }

    @staticmethod
    async def predict(history: list) -> dict:
        """
        Random Forest prediction: hours until next irrigation needed.
        Falls back to rule-based estimate if model not trained yet.
        """
        latest = history[0]
        moisture = latest.get("moisture", 50)
        temp     = latest.get("temperature", 28)

        # BUSINESS RULE: If already critical, return 0 immediately
        if moisture < MOISTURE_CRITICAL:
            return {
                "source": "business_rule",
                "irrigate_in_hours": 0.0,
                "confidence": "high",
                "current_moisture": moisture,
                "message": "Moisture already below critical threshold — irrigate now.",
            }

        # Try ML model
        if MODEL_PATH.exists():
            try:
                model = joblib.load(MODEL_PATH)
                # Feature vector: [moisture, temp, avg_moisture_trend]
                moistures = [h.get("moisture", 50) for h in history[:5]]
                trend = (moistures[0] - moistures[-1]) / len(moistures)  # drying rate
                X = np.array([[moisture, temp, trend]])
                hours = float(model.predict(X)[0])
                
                # Ensure prediction never goes negative
                hours = max(0.0, hours)
                
                return {
                    "source": "ml_model",
                    "irrigate_in_hours": round(hours, 1),
                    "confidence": "high",
                    "current_moisture": moisture,
                }
            except Exception as e:
                print(f"[IRRIGATION ML] Model error: {e} — using rule-based fallback.")

        # Rule-based fallback
        drying_rate = 2.0  # % per hour estimate
        if temp > 35:
            drying_rate = 3.5
        hours_until_critical = max(0, (moisture - MOISTURE_CRITICAL) / drying_rate)

        return {
            "source": "rule_based_fallback",
            "irrigate_in_hours": round(hours_until_critical, 1),
            "confidence": "medium",
            "current_moisture": moisture,
            "note": "Train ML model for higher accuracy — see ml/irrigation/train.py",
        }
