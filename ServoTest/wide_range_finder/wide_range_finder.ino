/*
  ServoTest/wide_range_finder.ino
  Sweeps all 16 PCA9685 channels from pulse 100 to 700.
  Watch each channel's output — note the pulse value when your servo starts moving.
*/

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

void sweepChannel(uint8_t ch) {
  Serial.print("\n=== CH");
  Serial.print(ch);
  Serial.println(" : Sweeping 100 -> 700 ===");
  Serial.println("Watch this channel's servo for movement.");

  for (int pulse = 100; pulse <= 700; pulse += 10) {
    pwm.setPWM(ch, 0, pulse);
    Serial.print("pulse=");
    Serial.println(pulse);
    delay(200);
  }

  // Park channel (stop signal)
  pwm.setPWM(ch, 0, 0);
  delay(500);
}

void setup() {
  Serial.begin(9600);
  Wire.begin();

  Serial.println("=== Full 16-Channel Wide Range Sweep ===");

  Wire.beginTransmission(0x40);
  if (Wire.endTransmission() != 0) {
    Serial.println("ERROR: PCA9685 not found at 0x40. Halting.");
    while (true) delay(1000);
  }
  Serial.println("PCA9685 found. Sweeping all 16 channels...");

  pwm.begin();
  pwm.setPWMFreq(50);
  delay(500);
}

void loop() {
  for (uint8_t ch = 0; ch < 16; ch++) {
    sweepChannel(ch);
  }
  Serial.println("\n=== All 16 channels done. Repeating in 3s... ===\n");
  delay(3000);
}
