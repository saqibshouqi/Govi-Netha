#include "SoilMoisture.h"

SoilMoisture::SoilMoisture(uint8_t pin) : _pin(pin) {}

void SoilMoisture::begin() {
  pinMode(_pin, INPUT);
}

float SoilMoisture::readRaw() {
  return analogRead(_pin);
}

float SoilMoisture::readMoisturePct() {
  int raw = analogRead(_pin);
  // Map: ADC_DRY → 0%, ADC_WET → 100%
  float pct = map(raw, ADC_DRY, ADC_WET, 0, 100);
  return constrain(pct, 0.0f, 100.0f);
}
