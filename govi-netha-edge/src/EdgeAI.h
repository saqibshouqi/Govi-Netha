#pragma once
#include <Arduino.h>
#include "config.h"

/**
 * EdgeAI — rule-based irrigation classifier running on the ESP32.
 *
 * This is the first version of the edge AI. For Day 2 we will
 * replace this with a TFLite Micro model. The interface stays
 * identical so the rest of the firmware does not change.
 *
 * Output states:
 *   0 = OK           — no action needed
 *   1 = IRRIGATE_SOON — action needed within 2-4 hours
 *   2 = IRRIGATE_NOW  — critical, irrigate immediately
 */
class EdgeAI
{
public:
    struct Result
    {
        int state;      // 0, 1, or 2
        String label;   // human-readable
        String message; // detailed message for serial output
    };

    static Result classify(float moisturePct, float tempC, float humidityPct)
    {
        Result r;

        if (moisturePct < MOISTURE_CRITICAL)
        {
            r.state = 2;
            r.label = "IRRIGATE_NOW";
            r.message = "CRITICAL — Moisture " + String(moisturePct, 1) +
                        "% is below " + String(MOISTURE_CRITICAL, 0) + "%. Irrigate immediately!";
        }
        else if (moisturePct < MOISTURE_WARNING && tempC > TEMP_HIGH_THRESHOLD)
        {
            r.state = 2;
            r.label = "IRRIGATE_NOW";
            r.message = "CRITICAL — Low moisture (" + String(moisturePct, 1) +
                        "%) combined with high temp (" + String(tempC, 1) + "°C). Irrigate NOW.";
        }
        else if (moisturePct < MOISTURE_WARNING)
        {
            r.state = 1;
            r.label = "IRRIGATE_SOON";
            r.message = "WARNING — Moisture " + String(moisturePct, 1) +
                        "% approaching threshold. Irrigate within 2-4 hours.";
        }
        else
        {
            r.state = 0;
            r.label = "OK";
            r.message = "OK — Moisture " + String(moisturePct, 1) + "% is healthy. No action needed.";
        }

        return r;
    }
};