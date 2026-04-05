#pragma once
/**
 * COMPONENT 1 — Smart Irrigation Optimization
 * Owner: Saqib
 *
 * Edge AI Logic:
 *   - Rule-based threshold detection for immediate alerts
 *   - Drying rate estimation from consecutive readings
 */
#include <Arduino.h>
#include "../../config.h"

class IrrigationEdge {
public:
  /**
   * Evaluate current moisture & temperature.
   * Prints alert to serial. Returns severity: 0=OK, 1=WARNING, 2=CRITICAL
   */
  static int evaluate(float moisturePct, float temperatureC) {
    Serial.print("  [IRRIGATION] ");

    if (moisturePct < IRRIGATION_MOISTURE_LOW_THRESHOLD) {
      Serial.printf("🚨 CRITICAL — Moisture %.1f%% (< %.0f%%). IRRIGATE NOW!\n",
                    moisturePct, IRRIGATION_MOISTURE_LOW_THRESHOLD);
      return 2;
    }

    if (moisturePct < IRRIGATION_MOISTURE_OK_THRESHOLD &&
        temperatureC > IRRIGATION_TEMP_HIGH_THRESHOLD) {
      Serial.printf("⚠️  WARNING — Moisture %.1f%% + High Temp %.1f°C. Irrigate soon.\n",
                    moisturePct, temperatureC);
      return 1;
    }

    if (moisturePct < IRRIGATION_MOISTURE_OK_THRESHOLD) {
      Serial.printf("ℹ️  MONITOR — Moisture %.1f%% slightly low.\n", moisturePct);
      return 1;
    }

    Serial.printf("✅ OK — Moisture %.1f%%\n", moisturePct);
    return 0;
  }
};
