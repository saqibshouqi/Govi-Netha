#pragma once
#include <Arduino.h>
#include <HardwareSerial.h>

/**
 * NPK Sensor — RS485 UART protocol
 * Common sensors: JXBS-3001-NPK, RS485 Soil NPK sensor
 * Uses UART2 on ESP32 (GPIO16=RX, GPIO17=TX)
 */
class NPKSensor {
public:
  NPKSensor(uint8_t rxPin, uint8_t txPin);
  void  begin();
  float readNitrogen();    // mg/kg
  float readPhosphorus();  // mg/kg
  float readPotassium();   // mg/kg

private:
  uint8_t _rxPin, _txPin;
  HardwareSerial _serial;

  // RS485 query command bytes (standard for most NPK sensors)
  static const uint8_t CMD_NITROGEN[];
  static const uint8_t CMD_PHOSPHORUS[];
  static const uint8_t CMD_POTASSIUM[];

  float sendQuery(const uint8_t* cmd, size_t len);
};
