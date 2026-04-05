#pragma once
/**
 * COMPONENT 4 — Crop Stress Detection
 * Owner: Roshana
 *
 * Edge AI Logic:
 *   - Computes a stress index (0–100) from temperature, humidity, moisture
 *   - Weighted formula: higher weight on temperature deviation
 */
#include <Arduino.h>
#include "../../config.h"

class StressEdge {
public:
  /**
   * Compute stress index 0–100.
   * 0–30: Low | 31–60: Medium | 61–100: High/Critical
   */
  static float computeStressIndex(float tempC, float humidityPct, float moisturePct) {
    float stressScore = 0.0f;

    // Temperature contribution (0–50 points)
    if (tempC > STRESS_TEMP_HIGH) {
      stressScore += min(50.0f, (tempC - STRESS_TEMP_HIGH) * 5.0f);
    } else if (tempC < STRESS_TEMP_LOW) {
      stressScore += min(50.0f, (STRESS_TEMP_LOW - tempC) * 5.0f);
    }

    // Humidity contribution (0–25 points)
    if (humidityPct < STRESS_HUMIDITY_LOW) {
      stressScore += min(25.0f, (STRESS_HUMIDITY_LOW - humidityPct) * 0.5f);
    }

    // Moisture contribution (0–25 points)
    if (moisturePct < 40.0f) {
      stressScore += min(25.0f, (40.0f - moisturePct) * 0.5f);
    }

    return constrain(stressScore, 0.0f, 100.0f);
  }

  static int evaluate(float tempC, float humidityPct, float moisturePct) {
    float idx = computeStressIndex(tempC, humidityPct, moisturePct);
    Serial.printf("  [STRESS] Index=%.1f/100 — ", idx);

    if (idx > STRESS_INDEX_CRITICAL) {
      Serial.println("🚨 CRITICAL STRESS — Immediate action required!");
      return 2;
    }
    if (idx > 30.0f) {
      Serial.println("⚠️  MEDIUM STRESS — Monitor closely.");
      return 1;
    }
    Serial.println("✅ LOW STRESS — Conditions acceptable.");
    return 0;
  }
};
