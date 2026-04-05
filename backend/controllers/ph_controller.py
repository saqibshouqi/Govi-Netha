"""
COMPONENT 3 — pH Controller
Owner: Ravisha
Business logic: pH status evaluation + regression-based correction plan
"""
import joblib
import numpy as np
from pathlib import Path

MODEL_PATH = Path(__file__).parent.parent / "ml" / "ph" / "model.pkl"

# Optimal pH range for paddy cultivation
PH_RANGES = {
    "critical_acidic":  (0.0, 4.5),
    "warning_acidic":   (4.5, 5.5),
    "optimal":          (5.5, 7.0),
    "warning_alkaline": (7.0, 8.0),
    "critical_alkaline":(8.0, 14.0),
}

class PHController:

    @staticmethod
    def _get_ph_status(ph: float) -> tuple[str, str]:
        if ph < 4.5: return "critical_acidic",  "critical"
        if ph < 5.5: return "warning_acidic",   "warning"
        if ph <= 7.0:return "optimal",           "normal"
        if ph <= 8.0:return "warning_alkaline",  "warning"
        return "critical_alkaline", "critical"

    @staticmethod
    def evaluate_status(doc: dict) -> dict:
        ph = doc.get("ph", 7.0)
        status, severity = PHController._get_ph_status(ph)

        messages = {
            "critical_acidic":   "Severely acidic — apply agricultural lime immediately.",
            "warning_acidic":    "Slightly acidic — consider liming to raise pH.",
            "optimal":           "pH is ideal for paddy cultivation.",
            "warning_alkaline":  "Slightly alkaline — monitor and consider acidifying agents.",
            "critical_alkaline": "Severely alkaline — apply elemental sulphur.",
        }

        return {
            "ph": ph,
            "status": status,
            "severity": severity,
            "message": messages[status],
            "optimal_range": "5.5 – 7.0",
            "timestamp": doc.get("created_at"),
        }

    @staticmethod
    async def correction_plan(history: list) -> dict:
        latest = history[0]
        ph = latest.get("ph", 7.0)
        status, _ = PHController._get_ph_status(ph)

        # Try ML regression model
        if MODEL_PATH.exists():
            try:
                model = joblib.load(MODEL_PATH)
                X = np.array([[ph]])
                kg_per_acre = float(model.predict(X)[0])
                return {
                    "source": "ml_model",
                    "current_ph": ph,
                    "target_ph": 6.5,
                    "amendment_kg_per_acre": round(kg_per_acre, 2),
                    "amendment_type": "Agricultural Lime" if ph < 5.5 else "Elemental Sulphur",
                }
            except Exception as e:
                print(f"[PH ML] Error: {e}")

        # Rule-based fallback
        if ph < 5.5:
            # ~2.5 tonnes/ha of lime raises pH by ~1 unit — simplified
            deficit = 6.5 - ph
            lime_kg = round(deficit * 500, 1)  # rough estimate per acre
            return {
                "source": "rule_based_fallback",
                "current_ph": ph, "target_ph": 6.5,
                "amendment": f"Apply ~{lime_kg} kg/acre of Agricultural Lime (CaCO₃).",
                "note": "Split application: 50% before tillage, 50% after.",
            }
        elif ph > 7.0:
            excess = ph - 6.5
            sulphur_kg = round(excess * 200, 1)
            return {
                "source": "rule_based_fallback",
                "current_ph": ph, "target_ph": 6.5,
                "amendment": f"Apply ~{sulphur_kg} kg/acre of Elemental Sulphur.",
                "note": "Incorporate into soil 2–3 weeks before planting.",
            }
        return {"source": "rule_based_fallback", "current_ph": ph, "message": "No correction needed."}
