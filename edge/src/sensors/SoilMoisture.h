#pragma once
#include <Arduino.h>

class SoilMoisture {
public:
  explicit SoilMoisture(uint8_t pin);
  void  begin();
  float readRaw();          // 0–4095 ADC value
  float readMoisturePct();  // 0–100 %
private:
  uint8_t _pin;
  // Calibrate these against your specific sensor in dry/wet soil
  static constexpr int ADC_DRY = 3200;
  static constexpr int ADC_WET = 1200;
};
