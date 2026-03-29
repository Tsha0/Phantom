/*
  ServoTest/calibrated_sweep.ino
  Step 2: Sweep each servo using its known-good calibrated pulse range.

  Uses the same pulse values as Phantom.ino (confirmed working calibration):
    CH0 PV  : 370 (0%) -> 520 (100%)
    CH1 CR1 : 150 (0%) -> 290 (100%)
    CH2 CR2 : 260 (0%) -> 410 (100%)

  Each servo sweeps 0% -> 50% -> 100% -> 50% -> 0% with 1.5s pauses.
  Serial output tells you exactly which servo/position is being commanded.

  WHY servo_test.ino failed:
    It used SERVOMIN=150, SERVOMAX=600.
    PV (CH0) valid range starts at 370 — pulse 150 is outside range, servo ignored it.
    CR2 (CH2) valid range starts at 260 — pulse 150 is also out of range.
*/

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Calibrated pulse ranges from Phantom.ino
const uint8_t  CHANNELS[3]  = {0,   7,   12};
const int      PULSE_MIN[3] = {370, 150, 260}; // 0%
const int      PULSE_MAX[3] = {520, 290, 410}; // 100%
const char*    NAMES[3]     = {"PV (CH0)", "CR1 (CH7)", "CR2 (CH12)"};

int percentToPulse(int idx, int pct) {
  pct = constrain(pct, 0, 100);
  return map(pct, 0, 100, PULSE_MIN[idx], PULSE_MAX[idx]);
}

void moveServo(int idx, int pct) {
  int pulse = percentToPulse(idx, pct);
  pwm.setPWM(CHANNELS[idx], 0, pulse);
  Serial.print(NAMES[idx]);
  Serial.print(" -> ");
  Serial.print(pct);
  Serial.print("% (pulse ");
  Serial.print(pulse);
  Serial.println(")");
}

void setup() {
  Serial.begin(9600);
  Wire.begin();

  Serial.println("=== Calibrated Servo Sweep Test ===");

  // Confirm PCA9685 on I2C
  Wire.beginTransmission(0x40);
  if (Wire.endTransmission() != 0) {
    Serial.println("ERROR: PCA9685 not found at 0x40. Check wiring. Halting.");
    while (true) delay(1000);
  }
  Serial.println("PCA9685 found. Starting sweep...\n");

  pwm.begin();
  pwm.setPWMFreq(50); // 50 Hz is standard for servos
  delay(500);
}

void loop() {
  const int steps[] = {0, 50, 100, 50, 0};
  const int stepCount = 5;

  for (int i = 0; i < 3; i++) {
    Serial.print("\n--- Testing ");
    Serial.print(NAMES[i]);
    Serial.println(" ---");

    for (int s = 0; s < stepCount; s++) {
      moveServo(i, steps[s]);
      delay(1500);
    }
  }

  Serial.println("\n=== Cycle complete. Repeating in 3s... ===\n");
  delay(3000);
}
