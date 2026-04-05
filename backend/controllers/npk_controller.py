"""
COMPONENT 2 — NPK Controller
Owner: Januki
Business logic: deficiency classification + fertilizer recommendation
"""
import joblib
import numpy as np
from pathlib import Path

MODEL_PATH = Path(__file__).parent.parent / "ml" / "npk" / "model.pkl"

# Optimal ranges for paddy (mid-to-late growth)
THRESHOLDS = {
    "nitrogen":   {"low": 50,  "optimal": 80,  "high": 120},
    "phosphorus": {"low": 25,  "optimal": 50,  "high": 80},
    "potassium":  {"low": 100, "optimal": 150, "high": 200},
}

FERTILIZER_ADVICE = {
    "nitrogen_low":   "Apply Urea (46-0-0) at 25 kg/acre. Split into 2 doses.",
    "phosphorus_low": "Apply Rock Phosphate or DAP (18-46-0) at 20 kg/acre.",
    "potassium_low":  "Apply Muriate of Potash (MOP) at 15 kg/acre.",
}

class NPKController:

    @staticmethod
    def _classify_level(value: float, thresholds: dict) -> str:
        if value < thresholds["low"]:    return "low"
        if value < thresholds["optimal"]:return "below_optimal"
        if value <= thresholds["high"]:  return "optimal"
        return "high"

    @staticmethod
    def evaluate_status(doc: dict) -> dict:
        n = doc.get("nitrogen", 0)
        p = doc.get("phosphorus", 0)
        k = doc.get("potassium", 0)

        n_status = NPKController._classify_level(n, THRESHOLDS["nitrogen"])
        p_status = NPKController._classify_level(p, THRESHOLDS["phosphorus"])
        k_status = NPKController._classify_level(k, THRESHOLDS["potassium"])

        deficiencies = []
        if n_status == "low": deficiencies.append("Nitrogen")
        if p_status == "low": deficiencies.append("Phosphorus")
        if k_status == "low": deficiencies.append("Potassium")

        severity = "critical" if len(deficiencies) >= 2 else \
                   "warning"  if len(deficiencies) == 1 else "normal"

        return {
            "severity": severity,
            "nitrogen":   {"value": n, "unit": "mg/kg", "status": n_status},
            "phosphorus": {"value": p, "unit": "mg/kg", "status": p_status},
            "potassium":  {"value": k, "unit": "mg/kg", "status": k_status},
            "deficiencies": deficiencies,
            "timestamp": doc.get("created_at"),
        }

    @staticmethod
    async def recommend(history: list) -> dict:
        latest = history[0]
        n = latest.get("nitrogen", 0)
        p = latest.get("phosphorus", 0)
        k = latest.get("potassium", 0)

        # Try ML model
        if MODEL_PATH.exists():
            try:
                model = joblib.load(MODEL_PATH)
                X = np.array([[n, p, k]])
                label = model.predict(X)[0]  # e.g. "apply_nitrogen"
                return {"source": "ml_model", "recommendation": label, "n": n, "p": p, "k": k}
            except Exception as e:
                print(f"[NPK ML] Error: {e}")

        # Rule-based fallback
        advice = []
        if n < THRESHOLDS["nitrogen"]["low"]:   advice.append(FERTILIZER_ADVICE["nitrogen_low"])
        if p < THRESHOLDS["phosphorus"]["low"]: advice.append(FERTILIZER_ADVICE["phosphorus_low"])
        if k < THRESHOLDS["potassium"]["low"]:  advice.append(FERTILIZER_ADVICE["potassium_low"])
        if not advice:
            advice.append("NPK levels are satisfactory. Maintain current fertilization schedule.")

        return {"source": "rule_based_fallback", "recommendations": advice, "n": n, "p": p, "k": k}
