#include "SoilPH.h"

SoilPH::SoilPH(uint8_t pin) : _pin(pin) {}

void SoilPH::begin() {
  pinMode(_pin, INPUT);
}

float SoilPH::readPH() {
  // Average 10 samples for stability
  long sum = 0;
  for (int i = 0; i < 10; i++) {
    sum += analogRead(_pin);
    delay(10);
  }
  float avgADC = sum / 10.0f;
  // Convert ADC (0-4095) to voltage (0-3.3V on ESP32)
  float voltage = avgADC * (3.3f / 4095.0f);
  // Linear mapping: pH = -5.70 * voltage + 21.34  (calibrate these!)
  float pH = -5.70f * voltage + 21.34f + _calibrationOffset;
  return constrain(pH, 0.0f, 14.0f);
}
