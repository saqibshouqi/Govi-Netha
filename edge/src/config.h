#pragma once

// ─────────────────────────────────────────────────────────────
// GOVI NETHA — Edge Configuration
// EDIT THIS FILE with your WiFi credentials and API endpoint
// ─────────────────────────────────────────────────────────────

// ── WiFi ──────────────────────────────────────────────────────
#define WIFI_SSID        "YOUR_WIFI_SSID"
#define WIFI_PASSWORD    "YOUR_WIFI_PASSWORD"

// ── Backend API ───────────────────────────────────────────────
// Use your PC's local IP when testing locally (check with ipconfig/ifconfig)
// Use your deployed Render/Railway URL in production
#define API_BASE_URL     "http://192.168.1.100:8000/api"
#define API_POST_SENSORS API_BASE_URL "/sensors/data"

// ── Sensor Pins ───────────────────────────────────────────────
#define PIN_SOIL_MOISTURE   34   // ADC pin (analog)
#define PIN_DHT             4    // DHT22 data pin
#define PIN_PH_SENSOR       35   // Analog pH sensor
// NPK sensor communicates via RS485/UART — set RX/TX pins
#define PIN_NPK_RX          16
#define PIN_NPK_TX          17

// ── Timing ────────────────────────────────────────────────────
#define SENSOR_READ_INTERVAL_MS   10000   // Read sensors every 10 seconds
#define CLOUD_SEND_INTERVAL_MS    60000   // Send to cloud every 60 seconds

// ─────────────────────────────────────────────────────────────
// COMPONENT 1 — Irrigation Thresholds (Saqib)
// ─────────────────────────────────────────────────────────────
#define IRRIGATION_MOISTURE_LOW_THRESHOLD   40.0f  // % — trigger critical alert
#define IRRIGATION_MOISTURE_OK_THRESHOLD    60.0f  // % — optimal lower bound
#define IRRIGATION_TEMP_HIGH_THRESHOLD      35.0f  // °C — high evaporation risk

// ─────────────────────────────────────────────────────────────
// COMPONENT 2 — NPK Thresholds (Januki)
// ─────────────────────────────────────────────────────────────
#define NPK_NITROGEN_LOW     50.0f   // mg/kg
#define NPK_PHOSPHORUS_LOW   25.0f   // mg/kg
#define NPK_POTASSIUM_LOW    100.0f  // mg/kg

// ─────────────────────────────────────────────────────────────
// COMPONENT 3 — pH Thresholds (Ravisha)
// ─────────────────────────────────────────────────────────────
#define PH_OPTIMAL_LOW    5.5f
#define PH_OPTIMAL_HIGH   7.0f
#define PH_CRITICAL_LOW   4.5f
#define PH_CRITICAL_HIGH  8.0f

// ─────────────────────────────────────────────────────────────
// COMPONENT 4 — Crop Stress Thresholds (Roshana)
// ─────────────────────────────────────────────────────────────
#define STRESS_TEMP_HIGH       38.0f   // °C
#define STRESS_TEMP_LOW        15.0f   // °C
#define STRESS_HUMIDITY_LOW    40.0f   // %
#define STRESS_INDEX_CRITICAL  70.0f   // 0–100 scale
