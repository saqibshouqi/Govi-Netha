"""
Integration-style tests for the sensors route.
These tests mock the database layer so no MongoDB connection is needed.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.fixture
def mock_db():
    """Returns a mock database with a mock sensor_readings collection."""
    db = MagicMock()
    db.sensor_readings.insert_one = AsyncMock(
        return_value=MagicMock(inserted_id="507f1f77bcf86cd799439011")
    )
    db.sensor_readings.find_one = AsyncMock(return_value={
        "_id": "507f1f77bcf86cd799439011",
        "moisture": 65.0,
        "temperature": 28.0,
        "humidity": 70.0,
        "edge_state": 0,
        "edge_label": "OK",
        "created_at": "2024-01-01T00:00:00",
    })
    db.alerts = MagicMock()
    db.alerts.insert_one = AsyncMock(return_value=MagicMock())
    return db


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_root_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "Govi Netha" in data["system"]


@pytest.mark.asyncio
async def test_ingest_sensor_data_valid_payload(mock_db):
    with patch("routes.sensors.get_db", return_value=mock_db):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/sensors/data", json={
                "moisture": 65.0,
                "temperature": 28.0,
                "humidity": 72.0,
                "edge_state": 0,
                "edge_label": "OK",
            })
    assert response.status_code == 201
    data = response.json()
    assert "inserted_id" in data
    assert data["status"] == "stored"
    assert "irrigation_status" in data


@pytest.mark.asyncio
async def test_ingest_sensor_data_invalid_moisture():
    """Moisture above 100% should be rejected by Pydantic validation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/sensors/data", json={
            "moisture": 105.0,
            "temperature": 28.0,
            "humidity": 72.0,
        })
    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_ingest_triggers_alert_when_critical(mock_db):
    """Critical moisture should cause an alert to be written."""
    with patch("routes.sensors.get_db", return_value=mock_db):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/sensors/data", json={
                "moisture": 30.0,   # below MOISTURE_CRITICAL=40
                "temperature": 28.0,
                "humidity": 70.0,
            })
    assert response.status_code == 201
    # Alert insert should have been called
    mock_db.alerts.insert_one.assert_called_once()