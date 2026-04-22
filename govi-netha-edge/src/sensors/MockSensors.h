#pragma once
#include <Arduino.h>

/**
 * MockSensors - generates realistic paddy field sensor data
 * for development and testing before physical sensors arrive.
 *
 * Simulates:
 *   - Soil moisture that slowly decreases over time (drying)
 *   - Temperature that varies with a daily pattern
 *   - Humidity that varies inversely with temperature
 *
 * Replace calls to MockSensors::read*() with real sensor reads
 * once hardware is available. No other code needs to change.
 */
class MockSensors
{
public:
    static float readMoisturePct()
    {
        // Simulate soil slowly drying over time
        // Starts around 70%, drifts down toward 30% over ~2 hours
        // Resets when it gets very low (simulates irrigation event)
        static float moisture = 70.0f;
        static unsigned long lastUpdate = 0;

        unsigned long now = millis();
        if (lastUpdate == 0)
            lastUpdate = now;

        float elapsedHours = (now - lastUpdate) / 3600000.0f;
        lastUpdate = now;

        // Drying rate: 2-4% per hour depending on temperature simulation
        moisture -= (2.5f + random(-10, 10) * 0.1f) * elapsedHours;

        // Add realistic sensor noise (±1.5%)
        moisture += (random(-30, 30) / 20.0f);

        // Simulate irrigation: reset when critically dry
        if (moisture < 25.0f)
        {
            moisture = 72.0f + random(0, 100) / 10.0f;
            Serial.println("[MOCK] Irrigation event simulated - moisture reset");
        }

        return constrain(moisture, 20.0f, 95.0f);
    }

    static float readTemperatureC()
    {
        // Simulate daily temperature cycle: 24–38°C
        // Peaks around midday, lower in morning/evening
        unsigned long secondsOfDay = (millis() / 1000) % 86400;
        float hourOfDay = secondsOfDay / 3600.0f;
        float baseTemp = 28.0f + 7.0f * sin((hourOfDay - 6.0f) * PI / 12.0f);
        // Add sensor noise (±0.3°C)
        return baseTemp + (random(-10, 10) / 33.3f);
    }

    static float readHumidityPct()
    {
        // Humidity inversely correlated with temperature
        float temp = readTemperatureC();
        float baseHumidity = 85.0f - (temp - 24.0f) * 1.5f;
        // Add sensor noise (±2%)
        return constrain(baseHumidity + (random(-40, 40) / 20.0f), 35.0f, 95.0f);
    }

    static void printStatus()
    {
        Serial.println("[MOCK] Using simulated sensor data.");
        Serial.println("[MOCK] Swap MockSensors calls for real sensor reads after hardware arrives.");
    }
};