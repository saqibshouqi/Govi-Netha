/**
 * GOVI NETHA — ESP32 Edge Firmware
 * main.cpp — Orchestration entry point
 *
 * Flow:
 *   1. Read all sensors
 *   2. Run each component's edge AI logic (thresholds / rules)
 *   3. Print alerts to serial
 *   4. POST telemetry to backend API every CLOUD_SEND_INTERVAL_MS
 */

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "config.h"
#include "sensors/SoilMoisture.h"
#include "sensors/TempHumidity.h"
#include "sensors/SoilPH.h"
#include "sensors/NPKSensor.h"
#include "components/irrigation/IrrigationEdge.h"
#include "components/npk/NPKEdge.h"
#include "components/ph/PHEdge.h"
#include "components/stress/StressEdge.h"

// ── Sensor objects ─────────────────────────────────────────────
SoilMoisture soilMoisture(PIN_SOIL_MOISTURE);
TempHumidity tempHumidity(PIN_DHT);
SoilPH soilPH(PIN_PH_SENSOR);
NPKSensor npkSensor(PIN_NPK_RX, PIN_NPK_TX);

// ── Timing ─────────────────────────────────────────────────────
unsigned long lastSensorRead = 0;
unsigned long lastCloudSend  = 0;

// ── Latest readings (shared state) ────────────────────────────
float moisturePct   = 0.0f;
float temperatureC  = 0.0f;
float humidityPct   = 0.0f;
float phValue       = 0.0f;
float nitrogen      = 0.0f;
float phosphorus    = 0.0f;
float potassium     = 0.0f;

// ── Function declarations ──────────────────────────────────────
void connectWifi();
void readAllSensors();
void runEdgeAI();
bool postToCloud();

// ──────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  Serial.println("\n=== GOVI NETHA EDGE DEVICE ===");

  soilMoisture.begin();
  tempHumidity.begin();
  soilPH.begin();
  npkSensor.begin();

  connectWifi();
}

// ──────────────────────────────────────────────────────────────
void loop() {
  unsigned long now = millis();

  // Read sensors at SENSOR_READ_INTERVAL_MS
  if (now - lastSensorRead >= SENSOR_READ_INTERVAL_MS) {
    lastSensorRead = now;
    readAllSensors();
    runEdgeAI();
  }

  // Send to cloud at CLOUD_SEND_INTERVAL_MS
  if (now - lastCloudSend >= CLOUD_SEND_INTERVAL_MS) {
    lastCloudSend = now;
    if (WiFi.status() == WL_CONNECTED) {
      postToCloud();
    } else {
      Serial.println("[WIFI] Disconnected — attempting reconnect...");
      connectWifi();
    }
  }
}

// ──────────────────────────────────────────────────────────────
void connectWifi() {
  Serial.printf("[WIFI] Connecting to %s", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\n[WIFI] Connected. IP: %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("\n[WIFI] Failed to connect — will retry on next cloud send.");
  }
}

// ──────────────────────────────────────────────────────────────
void readAllSensors() {
  moisturePct   = soilMoisture.readMoisturePct();
  temperatureC  = tempHumidity.readTemperature();
  humidityPct   = tempHumidity.readHumidity();
  phValue       = soilPH.readPH();
  nitrogen      = npkSensor.readNitrogen();
  phosphorus    = npkSensor.readPhosphorus();
  potassium     = npkSensor.readPotassium();

  Serial.println("── Sensor Readings ──────────────────────────");
  Serial.printf("  Moisture: %.1f%%  Temp: %.1f°C  Humidity: %.1f%%\n",
                moisturePct, temperatureC, humidityPct);
  Serial.printf("  pH: %.2f  N: %.1f  P: %.1f  K: %.1f\n",
                phValue, nitrogen, phosphorus, potassium);
}

// ──────────────────────────────────────────────────────────────
void runEdgeAI() {
  Serial.println("── Edge AI Results ──────────────────────────");

  // Component 1 — Irrigation (Saqib)
  IrrigationEdge::evaluate(moisturePct, temperatureC);

  // Component 2 — NPK (Januki)
  NPKEdge::evaluate(nitrogen, phosphorus, potassium);

  // Component 3 — pH (Ravisha)
  PHEdge::evaluate(phValue);

  // Component 4 — Stress (Roshana)
  StressEdge::evaluate(temperatureC, humidityPct, moisturePct);

  Serial.println("─────────────────────────────────────────────");
}

// ──────────────────────────────────────────────────────────────
bool postToCloud() {
  HTTPClient http;
  http.begin(API_POST_SENSORS);
  http.addHeader("Content-Type", "application/json");

  // Build JSON payload
  JsonDocument doc;
  doc["moisture"]    = moisturePct;
  doc["temperature"] = temperatureC;
  doc["humidity"]    = humidityPct;
  doc["ph"]          = phValue;
  doc["nitrogen"]    = nitrogen;
  doc["phosphorus"]  = phosphorus;
  doc["potassium"]   = potassium;

  String body;
  serializeJson(doc, body);

  int httpCode = http.POST(body);
  if (httpCode == 200 || httpCode == 201) {
    Serial.println("[CLOUD] Data sent successfully.");
    http.end();
    return true;
  } else {
    Serial.printf("[CLOUD] POST failed. HTTP code: %d\n", httpCode);
    http.end();
    return false;
  }
}
