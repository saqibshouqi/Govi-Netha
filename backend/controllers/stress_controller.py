"""
COMPONENT 4 — Crop Stress Controller
Owner: Roshana
Business logic: stress index calculation + yield risk prediction
"""
import joblib
import numpy as np
from pathlib import Path

MODEL_PATH = Path(__file__).parent.parent / "ml" / "stress" / "model.pkl"

class StressController:

    @staticmethod
    def _compute_stress_index(temp: float, humidity: float, moisture: float) -> float:
        score = 0.0
        # Temperature contribution (0–50)
        if temp > 38:   score += min(50, (temp - 38) * 5)
        elif temp < 15: score += min(50, (15 - temp) * 5)
        # Humidity contribution (0–25)
        if humidity < 40: score += min(25, (40 - humidity) * 0.5)
        # Moisture contribution (0–25)
        if moisture < 40: score += min(25, (40 - moisture) * 0.5)
        return round(min(score, 100.0), 1)

    @staticmethod
    def evaluate_stress(doc: dict) -> dict:
        temp     = doc.get("temperature", 28)
        humidity = doc.get("humidity", 70)
        moisture = doc.get("moisture", 60)

        index = StressController._compute_stress_index(temp, humidity, moisture)

        if index > 70:
            status, severity = "critical", "critical"
            message = "Critical crop stress — risk of significant yield loss."
        elif index > 30:
            status, severity = "medium", "warning"
            message = "Moderate stress detected — monitor and intervene if trend worsens."
        else:
            status, severity = "low", "normal"
            message = "Low stress — crop conditions are acceptable."

        return {
            "stress_index": index,
            "status": status,
            "severity": severity,
            "message": message,
            "contributing_factors": {
                "temperature": {"value": temp,     "unit": "°C", "status": "high" if temp > 35 else "normal"},
                "humidity":    {"value": humidity,  "unit": "%",  "status": "low"  if humidity < 40 else "normal"},
                "moisture":    {"value": moisture,  "unit": "%",  "status": "low"  if moisture < 40 else "normal"},
            },
            "timestamp": doc.get("created_at"),
        }

    @staticmethod
    async def predict_risk(history: list) -> dict:
        temps     = [h.get("temperature", 28) for h in history]
        humidities= [h.get("humidity", 70)    for h in history]
        moistures = [h.get("moisture", 60)    for h in history]

        avg_temp = np.mean(temps)
        avg_hum  = np.mean(humidities)
        avg_mois = np.mean(moistures)
        max_temp = np.max(temps)

        # Try ML model
        if MODEL_PATH.exists():
            try:
                model = joblib.load(MODEL_PATH)
                X = np.array([[avg_temp, avg_hum, avg_mois, max_temp]])
                risk_label = model.predict(X)[0]  # e.g. "high_risk"
                proba = model.predict_proba(X)[0].tolist() if hasattr(model, "predict_proba") else None
                return {
                    "source": "ml_model",
                    "risk_level": risk_label,
                    "probabilities": proba,
                    "avg_temperature": round(avg_temp, 1),
                    "avg_humidity": round(avg_hum, 1),
                }
            except Exception as e:
                print(f"[STRESS ML] Error: {e}")

        # Rule-based fallback
        current_index = StressController._compute_stress_index(avg_temp, avg_hum, avg_mois)
        trend = "worsening" if temps[0] > temps[-1] + 2 else "stable"

        recommendations = []
        if avg_temp > 35: recommendations.append("Consider shade nets or early-morning irrigation to reduce heat stress.")
        if avg_hum < 50:  recommendations.append("Increase irrigation frequency to improve field humidity.")
        if avg_mois < 50: recommendations.append("Maintain soil moisture above 60% during this growth stage.")
        if not recommendations: recommendations.append("Continue current practices and monitor daily.")

        return {
            "source": "rule_based_fallback",
            "risk_level": "high" if current_index > 70 else "medium" if current_index > 30 else "low",
            "stress_index": current_index,
            "trend": trend,
            "recommendations": recommendations,
        }
