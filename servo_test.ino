/*
  Minimal Arduino sketch for testing servo control via serial.

  Expects lines like: "s1,s2,s3,pumpL,pumpR,temp\n" where s1..s3 are 0-100 percent.
  The sketch maps those percentages to PWM pulse counts for three servos using
  the Adafruit PCA9685 driver (Adafruit_PWMServoDriver).

  Upload this to your Arduino (with the PCA9685 and servos connected), then
  run the pytest hardware test which writes strings matching this format.
*/

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVO1_PWM 0
#define SERVO2_PWM 1
#define SERVO3_PWM 2

void setup() {
  Serial.begin(9600);
  pwm.begin();
  pwm.setPWMFreq(60); // standard servo freq
  delay(10);
  Serial.println("ServoTestReady");
}

void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd.length() == 0) return;
    if (cmd.equalsIgnoreCase("READ")) {
      // Reply with a simple zeros line to indicate readiness
      Serial.println("0,0,0,0,0,0");
      continue;
    }
    adjustServosAndConditions(cmd);
    Serial.println("OK");
  }
}

void adjustServosAndConditions(String conditions) {
  int firstComma = conditions.indexOf(',');
  int secondComma = conditions.indexOf(',', firstComma + 1);
  int thirdComma = conditions.indexOf(',', secondComma + 1);

  if (firstComma == -1 || secondComma == -1 || thirdComma == -1) {
    Serial.println("ERR:bad_format");
    return;
  }

  int servo1Pos = conditions.substring(0, firstComma).toInt();
  int servo2Pos = conditions.substring(firstComma + 1, secondComma).toInt();
  int servo3Pos = conditions.substring(secondComma + 1, thirdComma).toInt();

  servo1Pos = constrain(servo1Pos, 0, 100);
  servo2Pos = constrain(servo2Pos, 0, 100);
  servo3Pos = constrain(servo3Pos, 0, 100);

  uint16_t pwm1 = map(servo1Pos, 0, 100, 370, 520);
  uint16_t pwm2 = map(servo2Pos, 0, 100, 150, 290);
  uint16_t pwm3 = map(servo3Pos, 0, 100, 260, 410);

  pwm.setPWM(SERVO1_PWM, 0, pwm1);
  pwm.setPWM(SERVO2_PWM, 0, pwm2);
  pwm.setPWM(SERVO3_PWM, 0, pwm3);

  // Debug output
  Serial.print("S:");
  Serial.print(servo1Pos);
  Serial.print(',');
  Serial.print(servo2Pos);
  Serial.print(',');
  Serial.print(servo3Pos);
  Serial.print(" -> ");
  Serial.print(pwm1);
  Serial.print(',');
  Serial.print(pwm2);
  Serial.print(',');
  Serial.println(pwm3);
}
