#pragma once

// WiFi credentials
#define WIFI_SSID "Dialog-4G-DA48"
#define WIFI_PASSWORD "60252615"

// API endpoint
#define API_BASE_URL "http://192.168.0.4:8000/api"
#define API_SENSORS_ENDPOINT API_BASE_URL "/sensors/data"

// Timing (milliseconds)
#define EDGE_READ_INTERVAL_MS 60000UL   // 1 minute
#define CLOUD_SEND_INTERVAL_MS 300000UL // 5 minutes

// Irrigation thresholds
// Used if you later want fallback rule-based logic
#define MOISTURE_CRITICAL 40.0f
#define MOISTURE_WARNING 60.0f
#define TEMP_HIGH_THRESHOLD 35.0f

// Output pins
#define LED_PIN 18    // External LED
#define BUZZER_PIN 19 // Buzzer signal pin

// Sensor pins
#define PIN_MOISTURE 34 // Soil sensor analog output
#define PIN_DHT 4       // DHT22 data pin