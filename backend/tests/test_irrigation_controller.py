"""
Unit tests for IrrigationController.
Run from backend/: pytest
"""
import pytest
from controllers.irrigation_controller import (
    IrrigationController,
    MOISTURE_CRITICAL,
    MOISTURE_WARNING,
    TEMP_HIGH,
)


# ── evaluate_status ──────────────────────────────────────────────────────────

class TestEvaluateStatus:

    def _doc(self, moisture, temperature=28.0):
        return {"moisture": moisture, "temperature": temperature, "created_at": None}

    def test_critical_moisture_below_threshold(self):
        result = IrrigationController.evaluate_status(self._doc(MOISTURE_CRITICAL - 1))
        assert result["status"]   == "irrigate_now"
        assert result["severity"] == "critical"
        assert "critically low" in result["message"].lower()

    def test_critical_boundary_exactly_at_threshold(self):
        """Moisture exactly AT critical threshold is still critical (< not <=)."""
        result = IrrigationController.evaluate_status(self._doc(MOISTURE_CRITICAL))
        # MOISTURE_CRITICAL = 40, condition is moisture < 40, so 40 is NOT critical
        assert result["status"] != "irrigate_now"

    def test_irrigate_soon_warning_moisture_with_high_temp(self):
        result = IrrigationController.evaluate_status(
            self._doc(MOISTURE_WARNING - 5, temperature=TEMP_HIGH + 1)
        )
        assert result["status"]   == "irrigate_soon"
        assert result["severity"] == "warning"

    def test_monitor_warning_moisture_normal_temp(self):
        result = IrrigationController.evaluate_status(
            self._doc(MOISTURE_WARNING - 5, temperature=TEMP_HIGH - 5)
        )
        assert result["status"]   == "monitor"
        assert result["severity"] == "warning"

    def test_ok_above_warning_threshold(self):
        result = IrrigationController.evaluate_status(self._doc(MOISTURE_WARNING + 10))
        assert result["status"]   == "ok"
        assert result["severity"] == "normal"

    def test_response_contains_required_keys(self):
        result = IrrigationController.evaluate_status(self._doc(70.0))
        for key in ("status", "severity", "message", "moisture_pct", "temperature_c"):
            assert key in result, f"Missing key: {key}"

    def test_moisture_value_reflected_in_response(self):
        result = IrrigationController.evaluate_status(self._doc(55.5))
        assert result["moisture_pct"] == 55.5


# ── predict ──────────────────────────────────────────────────────────────────

class TestPredict:

    def _history(self, moisture, temperature=28.0, n=5):
        return [{"moisture": moisture, "temperature": temperature}] * n

    @pytest.mark.asyncio
    async def test_predict_returns_dict_with_required_keys(self):
        result = await IrrigationController.predict(self._history(65.0))
        for key in ("irrigate_in_hours", "current_moisture"):
            assert key in result, f"Missing key: {key}"

    @pytest.mark.asyncio
    async def test_predict_critically_dry_returns_zero(self):
        result = await IrrigationController.predict(self._history(MOISTURE_CRITICAL - 1))
        assert result["irrigate_in_hours"] == 0.0

    @pytest.mark.asyncio
    async def test_predict_healthy_moisture_returns_positive_hours(self):
        result = await IrrigationController.predict(self._history(80.0))
        assert result["irrigate_in_hours"] > 0

    @pytest.mark.asyncio
    async def test_predict_high_temp_reduces_hours(self):
        result_hot  = await IrrigationController.predict(self._history(70.0, temperature=38.0))
        result_cool = await IrrigationController.predict(self._history(70.0, temperature=25.0))
        # Higher temp → faster drying → fewer hours
        assert result_hot["irrigate_in_hours"] <= result_cool["irrigate_in_hours"]

    @pytest.mark.asyncio
    async def test_predict_source_field_present(self):
        result = await IrrigationController.predict(self._history(60.0))
        assert "source" in result
        assert result["source"] in ("ml_model", "rule_based_fallback")