#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include "config.h"
#include "TFLiteInference.h"

// DHT sensor
DHT dht(PIN_DHT, DHT22);

// Global state
unsigned long lastEdgeRead = 0;
unsigned long lastCloudSend = 0;

float g_moisture = 0.0f;
float g_temperature = 0.0f;
float g_humidity = 0.0f;
int g_edgeState = 0;
String g_edgeLabel = "UNKNOWN";

void connectWiFi();
void doEdgeRead();
bool sendToCloud();

void setup()
{
    Serial.begin(115200);
    delay(1000);

    Serial.println("\n╔══════════════════════════════════════╗");
    Serial.println("║   GOVI NETHA — Edge Irrigation AI    ║");
    Serial.println("╚══════════════════════════════════════╝");
    Serial.println("");

    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);

    // Init DHT sensor
    dht.begin();
    delay(2000);  // DHT22 needs time to stabilize

    bool tflite_ok = TFLiteInference::init();
    if (tflite_ok)
    {
        Serial.println("[TFLITE] Model loaded successfully on ESP32.");
    }
    else
    {
        Serial.println("[TFLITE] Model failed — using rule-based fallback.");
    }

    Serial.println("");
    connectWiFi();
    doEdgeRead();
    lastEdgeRead = millis();
    lastCloudSend = millis();
}

void loop()
{
    unsigned long now = millis();

    if (now - lastEdgeRead >= EDGE_READ_INTERVAL_MS)
    {
        lastEdgeRead = now;
        doEdgeRead();
    }

    if (now - lastCloudSend >= CLOUD_SEND_INTERVAL_MS)
    {
        lastCloudSend = now;
        if (WiFi.status() == WL_CONNECTED)
        {
            sendToCloud();
        }
        else
        {
            Serial.println("[WIFI] Disconnected — attempting reconnect...");
            connectWiFi();
        }
    }
}

void connectWiFi()
{
    Serial.printf("[WIFI] Connecting to %s", WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30)
    {
        delay(500);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED)
    {
        Serial.printf("\n[WIFI] Connected. IP: %s\n\n",
                      WiFi.localIP().toString().c_str());
        digitalWrite(LED_PIN, HIGH);
        delay(200);
        digitalWrite(LED_PIN, LOW);
    }
    else
    {
        Serial.println("\n[WIFI] Connection failed. Will retry on next cloud send.\n");
    }
}

void doEdgeRead()
{
    Serial.println("── Edge Read ───────────────────────────────");

    // Read REAL sensors
    int soilRaw = analogRead(PIN_MOISTURE);
    g_moisture = map(soilRaw, 4095, 1500, 0, 100);
    g_moisture = constrain(g_moisture, 0, 100);
    g_temperature = dht.readTemperature();
    g_humidity = dht.readHumidity();

    // Check if DHT22 failed
    if (isnan(g_temperature) || isnan(g_humidity))
    {
        Serial.println("  [DHT22] FAILED - check wiring on GPIO4");
        g_temperature = 0.0f;
        g_humidity = 0.0f;
    }

    Serial.printf("  Moisture:    %.1f %%\n", g_moisture);
    Serial.printf("  Temperature: %.1f C\n", g_temperature);
    Serial.printf("  Humidity:    %.1f %%\n\n", g_humidity);

    // Run TFLite inference
    g_edgeState = TFLiteInference::predict(g_moisture, g_temperature, g_humidity);
    String labels[] = {"OK", "IRRIGATE_SOON", "IRRIGATE_NOW"};
    g_edgeLabel = labels[g_edgeState];
    Serial.printf("  [AI RESULT] State: %d (%s)\n", g_edgeState, g_edgeLabel.c_str());

    if (g_edgeState == 2)
    {
        for (int i = 0; i < 5; i++)
        {
            digitalWrite(LED_PIN, HIGH);
            delay(100);
            digitalWrite(LED_PIN, LOW);
            delay(100);
        }
        digitalWrite(LED_PIN, HIGH);
        Serial.println("  [LED] ON — critical alert");
    }
    else if (g_edgeState == 1)
    {
        digitalWrite(LED_PIN, HIGH);
        delay(500);
        digitalWrite(LED_PIN, LOW);
        Serial.println("  [LED] Single blink — warning");
    }
    else
    {
        digitalWrite(LED_PIN, LOW);
        Serial.println("  [LED] OFF — conditions normal");
    }

    Serial.println("────────────────────────────────────────────");
    Serial.println("");
}

bool sendToCloud()
{
    Serial.println("── Cloud Send ──────────────────────────────");

    HTTPClient http;
    http.begin(API_SENSORS_ENDPOINT);
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(10000);

    JsonDocument doc;
    doc["moisture"] = round(g_moisture * 10.0f) / 10.0f;
    doc["temperature"] = round(g_temperature * 10.0f) / 10.0f;
    doc["humidity"] = round(g_humidity * 10.0f) / 10.0f;
    doc["edge_state"] = g_edgeState;
    doc["edge_label"] = g_edgeLabel;

    String body;
    serializeJson(doc, body);
    Serial.println("  Payload: " + body);

    int httpCode = http.POST(body);

    if (httpCode == 200 || httpCode == 201)
    {
        Serial.printf("  [OK] HTTP %d — data stored in MongoDB\n", httpCode);
        for (int i = 0; i < 2; i++)
        {
            digitalWrite(LED_PIN, HIGH);
            delay(80);
            digitalWrite(LED_PIN, LOW);
            delay(80);
        }
        http.end();
        return true;
    }
    else
    {
        Serial.printf("  [ERROR] HTTP %d — check backend URL in config.h\n", httpCode);
        http.end();
        return false;
    }
}