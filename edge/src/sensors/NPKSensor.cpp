#include "NPKSensor.h"

// Standard RS485 Modbus RTU query commands for NPK sensor
const uint8_t NPKSensor::CMD_NITROGEN[]   = {0x01, 0x03, 0x00, 0x1E, 0x00, 0x01, 0xE4, 0x0C};
const uint8_t NPKSensor::CMD_PHOSPHORUS[] = {0x01, 0x03, 0x00, 0x1F, 0x00, 0x01, 0xB5, 0xCC};
const uint8_t NPKSensor::CMD_POTASSIUM[]  = {0x01, 0x03, 0x00, 0x20, 0x00, 0x01, 0x85, 0xC0};

NPKSensor::NPKSensor(uint8_t rxPin, uint8_t txPin)
  : _rxPin(rxPin), _txPin(txPin), _serial(2) {}

void NPKSensor::begin() {
  _serial.begin(9600, SERIAL_8N1, _rxPin, _txPin);
  delay(100);
}

float NPKSensor::sendQuery(const uint8_t* cmd, size_t len) {
  // Flush
  while (_serial.available()) _serial.read();

  _serial.write(cmd, len);
  delay(200);  // Wait for response

  if (_serial.available() >= 7) {
    uint8_t buf[7];
    _serial.readBytes(buf, 7);
    // Response: [addr][func][bytes][high][low][crc_h][crc_l]
    return (float)((buf[3] << 8) | buf[4]);
  }
  Serial.println("[NPK] No response — check wiring");
  return 0.0f;
}

float NPKSensor::readNitrogen()   { return sendQuery(CMD_NITROGEN,   8); }
float NPKSensor::readPhosphorus() { return sendQuery(CMD_PHOSPHORUS, 8); }
float NPKSensor::readPotassium()  { return sendQuery(CMD_POTASSIUM,  8); }
