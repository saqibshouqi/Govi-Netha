#pragma once
#include <Arduino.h>
#include <DHT.h>

class TempHumidity {
public:
  explicit TempHumidity(uint8_t pin, uint8_t type = DHT22);
  void  begin();
  float readTemperature();  // °C
  float readHumidity();     // %
private:
  DHT _dht;
};
