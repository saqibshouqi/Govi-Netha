#pragma once
#include <Arduino.h>

class SoilPH {
public:
  explicit SoilPH(uint8_t pin);
  void  begin();
  float readPH();   // returns pH value (0–14)
private:
  uint8_t _pin;
  // Calibration offset — adjust after 2-point calibration with buffer solutions
  float _calibrationOffset = 0.0f;
};
