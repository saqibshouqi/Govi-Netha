"""
COMPONENT 3 — pH Controller
Owner: Ravisha

Business logic:
- pH status evaluation
- ML-based or rule-based soil correction plan
"""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np

# Initialize logger (better than print for production)
logger = logging.getLogger(__name__)

# Path to trained ML model
MODEL_PATH = Path(__file__).parent.parent / "ml" / "ph" / "model.pkl"

# Target pH for paddy cultivation
TARGET_PH = 6.5

# Optimal pH range
OPTIMAL_RANGE = (5.5, 7.0)

# pH classification ranges
PH_RANGES: dict[str, tuple[float, float]] = {
    "critical_acidic": (0.0, 4.5),
    "warning_acidic": (4.5, 5.5),
    "optimal": (5.5, 7.0),
    "warning_alkaline": (7.0, 8.0),
    "critical_alkaline": (8.0, 14.0),
}

# User-friendly messages for each pH status
STATUS_MESSAGES: dict[str, str] = {
    "critical_acidic": "Severely acidic — apply agricultural lime immediately.",
    "warning_acidic": "Slightly acidic — consider liming to raise pH.",
    "optimal": "pH is ideal for paddy cultivation.",
    "warning_alkaline": "Slightly alkaline — monitor and consider acidifying agents.",
    "critical_alkaline": "Severely alkaline — apply elemental sulphur.",
}


class PHController:
    """Handles pH status evaluation and correction recommendations."""

    @staticmethod
    def _normalize_ph(value: Any, default: float = 7.0) -> float:
        """
        STEP 1: Normalize input pH
        - Convert input to float
        - Ensure it is within valid range (0–14)
        - If invalid, return default value (7.0)
        """
        try:
            ph = float(value)
            if 0.0 <= ph <= 14.0:
                return ph
        except (TypeError, ValueError):
            pass
        return default

    @staticmethod
    def _get_ph_status(ph: float) -> tuple[str, str]:
        """
        STEP 2: Determine pH status category and severity
        Returns:
            status (str), severity (str)
        """
        if ph < 4.5:
            return "critical_acidic", "critical"
        if ph < 5.5:
            return "warning_acidic", "warning"
        if ph <= 7.0:
            return "optimal", "normal"
        if ph <= 8.0:
            return "warning_alkaline", "warning"
        return "critical_alkaline", "critical"

    @staticmethod
    def evaluate_status(doc: dict[str, Any]) -> dict[str, Any]:
        """
        STEP 3: Evaluate soil pH status

        Input:
            doc = {"ph": value, "created_at": timestamp}

        Output:
            Dictionary with status, severity, and message
        """

        # Extract and normalize pH value
        ph = PHController._normalize_ph(doc.get("ph"))

        # Determine status and severity
        status, severity = PHController._get_ph_status(ph)

        # Return structured response
        return {
            "ph": ph,
            "status": status,
            "severity": severity,
            "message": STATUS_MESSAGES[status],
            "optimal_range": f"{OPTIMAL_RANGE[0]} – {OPTIMAL_RANGE[1]}",
            "timestamp": doc.get("created_at"),
        }

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_model():
        """
        STEP 4: Load ML model (cached)

        - Loads model only once (performance optimization)
        - Returns None if model not available
        """
        if not MODEL_PATH.exists():
            return None

        try:
            return joblib.load(MODEL_PATH)
        except Exception:
            logger.exception("Failed to load pH ML model from %s", MODEL_PATH)
            return None

    @staticmethod
    def _rule_based_plan(ph: float) -> dict[str, Any]:
        """
        STEP 5: Rule-based fallback correction

        Used when:
        - ML model is unavailable
        - ML prediction fails
        """

        # Case 1: Soil is acidic → apply lime
        if ph < OPTIMAL_RANGE[0]:
            deficit = TARGET_PH - ph  # how much pH needs to increase

            # Approximation: 500 kg/acre raises pH by ~1 unit
            lime_kg = round(max(deficit, 0) * 500, 1)

            return {
                "source": "rule_based_fallback",
                "current_ph": ph,
                "target_ph": TARGET_PH,
                "amendment_needed": lime_kg > 0,
                "amendment_type": "Agricultural Lime",
                "amendment_kg_per_acre": lime_kg,
                "application_note": "Split application: 50% before tillage, 50% after.",
            }

        # Case 2: Soil is alkaline → apply sulphur
        if ph > OPTIMAL_RANGE[1]:
            excess = ph - TARGET_PH  # how much pH needs to decrease

            # Approximation: 200 kg/acre lowers pH by ~1 unit
            sulphur_kg = round(max(excess, 0) * 200, 1)

            return {
                "source": "rule_based_fallback",
                "current_ph": ph,
                "target_ph": TARGET_PH,
                "amendment_needed": sulphur_kg > 0,
                "amendment_type": "Elemental Sulphur",
                "amendment_kg_per_acre": sulphur_kg,
                "application_note": "Incorporate into soil 2–3 weeks before planting.",
            }

        # Case 3: Already optimal → no action needed
        return {
            "source": "rule_based_fallback",
            "current_ph": ph,
            "target_ph": TARGET_PH,
            "amendment_needed": False,
            "amendment_type": None,
            "amendment_kg_per_acre": 0.0,
            "application_note": "No correction needed.",
        }

    @staticmethod
    async def correction_plan(history: list[dict[str, Any]]) -> dict[str, Any]:
        """
        STEP 6: Generate correction plan

        Flow:
        1. Get latest pH from history
        2. Try ML model prediction
        3. If ML fails → fallback to rule-based method
        """

        # Safety check: ensure history is not empty
        if not history:
            return {
                "source": "none",
                "message": "No pH history available.",
            }

        # Get latest record
        latest = history[0]

        # Normalize pH value
        ph = PHController._normalize_ph(latest.get("ph"))

        # Try loading ML model
        model = PHController._load_model()

        if model is not None:
            try:
                # Prepare input for model
                X = np.array([[ph]])

                # Predict required amendment
                prediction = float(model.predict(X)[0])

                # Prevent negative values
                kg_per_acre = round(max(prediction, 0.0), 2)

                # Determine amendment type based on pH
                if ph < OPTIMAL_RANGE[0]:
                    amendment_type = "Agricultural Lime"
                elif ph > OPTIMAL_RANGE[1]:
                    amendment_type = "Elemental Sulphur"
                else:
                    amendment_type = None

                return {
                    "source": "ml_model",
                    "current_ph": ph,
                    "target_ph": TARGET_PH,
                    "amendment_needed": amendment_type is not None and kg_per_acre > 0,
                    "amendment_type": amendment_type,
                    "amendment_kg_per_acre": kg_per_acre if amendment_type else 0.0,
                    "application_note": "No correction needed." if amendment_type is None else None,
                }

            except Exception:
                # Log error and fallback
                logger.exception("Prediction failed in pH ML model")

        # Fallback if ML not available or failed
        return PHController._rule_based_plan(ph)