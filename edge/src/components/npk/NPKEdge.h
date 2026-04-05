#pragma once
/**
 * COMPONENT 2 — Soil Nutrient (NPK) Deficiency Detection
 * Owner: Januki
 *
 * Edge AI Logic:
 *   - Threshold-based deficiency detection
 *   - Returns a deficiency bitmask for quick cloud communication
 */
#include <Arduino.h>
#include "../../config.h"

class NPKEdge {
public:
  // Deficiency bitmask values
  static constexpr uint8_t DEFICIENCY_NONE       = 0b000;
  static constexpr uint8_t DEFICIENCY_NITROGEN   = 0b001;
  static constexpr uint8_t DEFICIENCY_PHOSPHORUS = 0b010;
  static constexpr uint8_t DEFICIENCY_POTASSIUM  = 0b100;

  /**
   * Check NPK levels against thresholds.
   * Returns bitmask of deficiencies detected.
   */
  static uint8_t evaluate(float nitrogen, float phosphorus, float potassium) {
    Serial.print("  [NPK] ");
    uint8_t mask = DEFICIENCY_NONE;

    if (nitrogen   < NPK_NITROGEN_LOW)   mask |= DEFICIENCY_NITROGEN;
    if (phosphorus < NPK_PHOSPHORUS_LOW) mask |= DEFICIENCY_PHOSPHORUS;
    if (potassium  < NPK_POTASSIUM_LOW)  mask |= DEFICIENCY_POTASSIUM;

    if (mask == DEFICIENCY_NONE) {
      Serial.printf("✅ OK — N:%.1f P:%.1f K:%.1f\n", nitrogen, phosphorus, potassium);
    } else {
      if (mask & DEFICIENCY_NITROGEN)
        Serial.printf("⚠️  LOW NITROGEN (%.1f mg/kg)  ", nitrogen);
      if (mask & DEFICIENCY_PHOSPHORUS)
        Serial.printf("⚠️  LOW PHOSPHORUS (%.1f mg/kg)  ", phosphorus);
      if (mask & DEFICIENCY_POTASSIUM)
        Serial.printf("⚠️  LOW POTASSIUM (%.1f mg/kg)  ", potassium);
      Serial.println();
    }
    return mask;
  }
};
