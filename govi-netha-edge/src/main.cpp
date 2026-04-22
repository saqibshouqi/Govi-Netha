#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include "config.h"
#include "TFLiteInference.h"

// DHT22 SENSOR OBJECT
DHT dht(PIN_DHT, DHT22);

// GLOBAL VARIABLES
// Track time for periodic sensor reading and cloud sending
unsigned long lastEdgeRead = 0;
unsigned long lastCloudSend = 0;

// Store latest sensor values and AI prediction
float g_moisture = 0.0f;
float g_temperature = 0.0f;
float g_humidity = 0.0f;
int g_edgeState = 0;
String g_edgeLabel = "UNKNOWN";

// FUNCTION DECLARATIONS
void connectWiFi();
void doEdgeRead();
bool sendToCloud();

// SETUP
void setup()
{
    Serial.begin(115200);
    delay(1000);

    Serial.println("\n╔══════════════════════════════════════╗");
    Serial.println("║   GOVI NETHA - Edge Irrigation AI    ║");
    Serial.println("╚══════════════════════════════════════╝");
    Serial.println("");

    // Set LED and buzzer pins as output
    pinMode(LED_PIN, OUTPUT);
    pinMode(BUZZER_PIN, OUTPUT);

    // Start with LED and buzzer OFF
    digitalWrite(LED_PIN, LOW);
    digitalWrite(BUZZER_PIN, LOW);

    // Start DHT22
    dht.begin();
    delay(2000); // DHT22 needs time to stabilize

    // Initialize TFLite model
    bool tflite_ok = TFLiteInference::init();
    if (tflite_ok)
    {
        Serial.println("[TFLITE] Model loaded successfully on ESP32.");
    }
    else
    {
        Serial.println("[TFLITE] Model failed - using rule-based fallback.");
    }

    Serial.println("");

    // Connect to WiFi
    connectWiFi();

    // Run one sensor read immediately at startup
    doEdgeRead();

    // Save current time
    lastEdgeRead = millis();
    lastCloudSend = millis();
}

// LOOP
void loop()
{
    unsigned long now = millis();

    // Run edge reading + AI at interval
    if (now - lastEdgeRead >= EDGE_READ_INTERVAL_MS)
    {
        lastEdgeRead = now;
        doEdgeRead();
    }

    // Send to cloud at interval
    if (now - lastCloudSend >= CLOUD_SEND_INTERVAL_MS)
    {
        lastCloudSend = now;

        if (WiFi.status() == WL_CONNECTED)
        {
            sendToCloud();
        }
        else
        {
            Serial.println("[WIFI] Disconnected - attempting reconnect...");
            connectWiFi();
        }
    }
}

// WIFI CONNECTION
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

        // Small blink to show WiFi connected
        digitalWrite(LED_PIN, HIGH);
        delay(200);
        digitalWrite(LED_PIN, LOW);
    }
    else
    {
        Serial.println("\n[WIFI] Connection failed. Will retry later.\n");
    }
}

// SENSOR READING + AI LOGIC
void doEdgeRead()
{
    Serial.println("── Edge Read ───────────────────────────────");

    // Read soil moisture sensor
    int soilRaw = analogRead(PIN_MOISTURE);

    // Convert raw value to moisture percentage
    // Calibration: DRY_VALUE = sensor reading in open air (adjust after calibration)
    //              WET_VALUE  = sensor reading submerged in water (adjust after calibration)
    // To calibrate: read soilRaw in air → that is your DRY_VALUE
    //               read soilRaw in a cup of water → that is your WET_VALUE
    const int DRY_VALUE = 2811; // adjust this after reading soilRaw in open air
    const int WET_VALUE = 1134; // adjust this after reading soilRaw in water

    g_moisture = (float)(soilRaw - WET_VALUE) / (float)(DRY_VALUE - WET_VALUE) * 100.0f;
    g_moisture = 100.0f - g_moisture; // invert: low raw = wet = high %
    g_moisture = constrain(g_moisture, 0.0f, 100.0f);

    // Read temperature and humidity from DHT22
    g_temperature = dht.readTemperature();
    g_humidity = dht.readHumidity();

    // Handle DHT read failure
    if (isnan(g_temperature) || isnan(g_humidity))
    {
        Serial.println("  [DHT22] FAILED - using last known values");
        // g_temperature and g_humidity keep their previous global values
        // Only reset on first boot if both are still 0
        if (g_temperature == 0.0f)
            g_temperature = 28.0f; // safe Sri Lanka default
        if (g_humidity == 0.0f)
            g_humidity = 70.0f;
    }

    // Print sensor values
    Serial.printf("  Soil Raw:     %d\n", soilRaw);
    Serial.printf("  Moisture:     %.1f %%\n", g_moisture);
    Serial.printf("  Temperature:  %.1f C\n", g_temperature);
    Serial.printf("  Humidity:     %.1f %%\n\n", g_humidity);

    // Run TFLite model
    g_edgeState = TFLiteInference::predict(g_moisture, g_temperature, g_humidity);

    // Convert class number to label
    String labels[] = {"OK", "IRRIGATE_SOON", "IRRIGATE_NOW"};
    g_edgeLabel = labels[g_edgeState];

    Serial.printf("  [AI RESULT] State: %d (%s)\n", g_edgeState, g_edgeLabel.c_str());

    // DEMO ALERT LOGIC
    // OK              -> LED OFF, buzzer OFF
    // IRRIGATE_SOON   -> Slow blink + slow beep
    // IRRIGATE_NOW    -> Fast blink + fast beep

    if (g_edgeState == 2)
    {
        // FAST blink for IRRIGATE_NOW
        Serial.println("  [ALERT] IRRIGATE_NOW - FAST blink + beep");

        for (int i = 0; i < 6; i++)
        {
            digitalWrite(LED_PIN, HIGH);
            digitalWrite(BUZZER_PIN, HIGH);
            delay(150);

            digitalWrite(LED_PIN, LOW);
            digitalWrite(BUZZER_PIN, LOW);
            delay(150);
        }
    }
    else if (g_edgeState == 1)
    {
        // SLOW blink for IRRIGATE_SOON
        Serial.println("  [ALERT] IRRIGATE_SOON - SLOW blink + beep");

        for (int i = 0; i < 3; i++)
        {
            digitalWrite(LED_PIN, HIGH);
            digitalWrite(BUZZER_PIN, HIGH);
            delay(500);

            digitalWrite(LED_PIN, LOW);
            digitalWrite(BUZZER_PIN, LOW);
            delay(500);
        }
    }
    else
    {
        // OK condition
        digitalWrite(LED_PIN, LOW);
        digitalWrite(BUZZER_PIN, LOW);

        Serial.println("  [ALERT] OK - LED OFF, buzzer OFF");
    }

    Serial.println("────────────────────────────────────────────");
    Serial.println("");
}

// SEND DATA TO CLOUD
bool sendToCloud()
{
    Serial.println("── Cloud Send ──────────────────────────────");

    HTTPClient http;
    http.begin(API_SENSORS_ENDPOINT);
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(10000);

    // Build JSON payload
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
        Serial.printf("  [OK] HTTP %d - data stored in MongoDB\n", httpCode);
        http.end();
        return true;
    }
    else
    {
        Serial.printf("  [ERROR] HTTP %d - check backend URL in config.h\n", httpCode);
        http.end();
        return false;
    }
}