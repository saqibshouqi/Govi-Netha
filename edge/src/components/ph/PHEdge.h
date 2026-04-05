#pragma once
/**
 * COMPONENT 3 — Soil pH Monitoring
 * Owner: Ravisha
 *
 * Edge AI Logic:
 *   - Detects optimal / warning / critical pH ranges for paddy
 *   - Immediate serial alert; correction details handled in cloud
 */
#include <Arduino.h>
#include "../../config.h"

class PHEdge {
public:
  enum class PHStatus { CRITICAL_ACIDIC, WARNING_ACIDIC, OPTIMAL, WARNING_ALKALINE, CRITICAL_ALKALINE };

  static PHStatus evaluate(float ph) {
    Serial.printf("  [PH] pH=%.2f — ", ph);

    if (ph < PH_CRITICAL_LOW) {
      Serial.println("🚨 CRITICAL — Severely Acidic! Apply lime immediately.");
      return PHStatus::CRITICAL_ACIDIC;
    }
    if (ph < PH_OPTIMAL_LOW) {
      Serial.println("⚠️  WARNING — Slightly Acidic. Monitor and consider liming.");
      return PHStatus::WARNING_ACIDIC;
    }
    if (ph > PH_CRITICAL_HIGH) {
      Serial.println("🚨 CRITICAL — Severely Alkaline! Apply sulphur.");
      return PHStatus::CRITICAL_ALKALINE;
    }
    if (ph > PH_OPTIMAL_HIGH) {
      Serial.println("⚠️  WARNING — Slightly Alkaline. Monitor closely.");
      return PHStatus::WARNING_ALKALINE;
    }

    Serial.println("✅ OPTIMAL — pH in ideal range for paddy.");
    return PHStatus::OPTIMAL;
  }
};
