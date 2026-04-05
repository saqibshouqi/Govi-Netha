#include "TempHumidity.h"

TempHumidity::TempHumidity(uint8_t pin, uint8_t type) : _dht(pin, type) {}

void TempHumidity::begin() { _dht.begin(); }

float TempHumidity::readTemperature() {
  float t = _dht.readTemperature();
  return isnan(t) ? -1.0f : t;
}

float TempHumidity::readHumidity() {
  float h = _dht.readHumidity();
  return isnan(h) ? -1.0f : h;
}
