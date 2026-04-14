#pragma once

// ── WiFi credentials ───────────────────────────────────────
#define WIFI_SSID "Dialog-JM01A-08C3"
#define WIFI_PASSWORD "69490641"

// ── API endpoint ───────────────────────────────────────────
// During development use your PC's local IP address
// e.g. "http://192.168.1.45:8000/api"
// Once deployed to Render, replace with your Render URL
// e.g. "https://govi-netha-api.onrender.com/api"
#define API_BASE_URL "http://192.168.0.2:8000/api"
#define API_SENSORS_ENDPOINT API_BASE_URL "/sensors/data"

// ── Timing (milliseconds) ──────────────────────────────────
#define EDGE_READ_INTERVAL_MS 60000UL   // 1 minute  — edge reads + inference
#define CLOUD_SEND_INTERVAL_MS 300000UL // 5 minutes — send to MongoDB

// ── Irrigation thresholds ──────────────────────────────────
#define MOISTURE_CRITICAL 40.0f   // below this → IRRIGATE_NOW
#define MOISTURE_WARNING 60.0f    // below this → IRRIGATE_SOON
#define TEMP_HIGH_THRESHOLD 35.0f // above this worsens urgency
#define LED_PIN 2                 // GPIO2

// ── Sensor pins (used when real sensors arrive) ────────────
#define PIN_MOISTURE 34 // GPIO34 — ADC1, WiFi-safe
#define PIN_DHT 4       // GPIO4  — DHT22 data