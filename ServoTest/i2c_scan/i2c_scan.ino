/*
  ServoTest/i2c_scan.ino
  Step 1: Confirm the PCA9685 is visible on the I2C bus.
  Expected output: "I2C device found at 0x40" and "PCA9685 FOUND"
  If not found: check SDA (A4), SCL (A5), VCC, and GND wiring.
*/

#include <Wire.h>

void setup() {
  Serial.begin(9600);
  Wire.begin();
  delay(500);

  Serial.println("=== I2C Bus Scan ===");

  int found = 0;
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    uint8_t err = Wire.endTransmission();
    if (err == 0) {
      Serial.print("I2C device found at 0x");
      if (addr < 16) Serial.print("0");
      Serial.println(addr, HEX);
      found++;
    }
  }

  if (found == 0) {
    Serial.println("No I2C devices found.");
    Serial.println("Check: SDA->A4, SCL->A5, VCC->5V, GND->GND");
  }

  // Check specifically for PCA9685
  Wire.beginTransmission(0x40);
  if (Wire.endTransmission() == 0) {
    Serial.println("PCA9685 FOUND at 0x40 - wiring OK");
  } else {
    Serial.println("PCA9685 NOT found at 0x40 - check wiring!");
  }
}

void loop() {
  // Nothing - one-shot scan
}
