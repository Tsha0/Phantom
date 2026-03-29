/*
  Phantom — Dynamic Ventricular Phantom firmware

  Servo motors (PCA9685 I2C PWM driver):
    CR1 (ch 0)    CR2 (ch 1)    CR3 (ch 2)    CR4 (ch 3)

  Flow sensors (digital interrupt, YF-S401 — 5880 pulses/L):
    FL1 — pin 8    FL2 — pin 7    FL3 — pin 5    FL4 — pin 3

  Pressure sensors (analog, 0-10 PSI, 0.5-4.5 V output):
    P1 — A0    P2 — A1    P3 — A2    P4 — A3

  Serial protocol:
    RX  "READ\n"                              → TX sensor CSV
    RX  "cr1,cr2,cr3,cr4,...\n"               → adjust servos (0-100 %)
    TX  "fl1,fl2,fl3,fl4,p1,p2,p3,p4\n"      → CSV in L/min and mmHg
*/

#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVO_CR1 0
#define SERVO_CR2 1
#define SERVO_CR3 2
#define SERVO_CR4 3

const int flowSensorPins[] = {8, 7, 5, 3};
const int pressureSensorPins[] = {A0, A1, A2, A3};

// Servo pulse ranges (0% → min, 100% → max)
const int servoPulseMin[] = {370, 150, 260, 260};
const int servoPulseMax[] = {520, 290, 410, 410};

const float PULSES_PER_LITER = 5880.0;
const float PSI_TO_MMHG = 51.715;
const float PSI_MAX = 10.0;
const float V_MIN = 0.5;
const float V_MAX = 4.5;
const float VCC = 5.0;

volatile int pulseCount[] = {0, 0, 0, 0};

void pulseCounterFL1() { pulseCount[0]++; }
void pulseCounterFL2() { pulseCount[1]++; }
void pulseCounterFL3() { pulseCount[2]++; }
void pulseCounterFL4() { pulseCount[3]++; }

typedef void (*ISR_FUNC)();
ISR_FUNC isrFuncs[] = {pulseCounterFL1, pulseCounterFL2, pulseCounterFL3, pulseCounterFL4};

void setup() {
  Serial.begin(9600);
  pwm.begin();
  pwm.setPWMFreq(60);

  for (int i = 0; i < 4; i++) {
    pinMode(flowSensorPins[i], INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(flowSensorPins[i]), isrFuncs[i], RISING);
  }
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    if (command == "READ") {
      readAndSendSensorData();
    } else {
      adjustServos(command);
    }
  }
}

void readAndSendSensorData() {
  for (int i = 0; i < 4; i++) pulseCount[i] = 0;

  interrupts();
  delay(1000);
  noInterrupts();

  String out = "";
  for (int i = 0; i < 4; i++) {
    float flow = max(pulseCount[i] / (PULSES_PER_LITER / 60.0), 0.0);
    if (i > 0) out += ",";
    out += String(flow);
  }
  for (int i = 0; i < 4; i++) {
    out += ",";
    out += String(max(readPressureSensor(pressureSensorPins[i]), 0.0));
  }
  Serial.println(out);
}

float readPressureSensor(int pin) {
  int sensorValue = analogRead(pin);
  float voltage = sensorValue * (VCC / 1023.0);

  float psi;
  if (voltage <= V_MIN) {
    psi = 0.0;
  } else if (voltage >= V_MAX) {
    psi = PSI_MAX;
  } else {
    psi = (voltage - V_MIN) * PSI_MAX / (V_MAX - V_MIN);
  }

  return psi * PSI_TO_MMHG;
}

void adjustServos(String conditions) {
  // Parse up to 4 comma-separated servo percentages
  int pos[4] = {0, 0, 0, 0};
  int start = 0;
  for (int i = 0; i < 4; i++) {
    int comma = conditions.indexOf(',', start);
    if (comma == -1 && i < 3) {
      // Fewer than 4 values — use what we have
      pos[i] = conditions.substring(start).toInt();
      break;
    }
    if (i < 3) {
      pos[i] = conditions.substring(start, comma).toInt();
      start = comma + 1;
    } else {
      pos[i] = conditions.substring(start).toInt();
    }
  }

  for (int i = 0; i < 4; i++) {
    pos[i] = constrain(pos[i], 0, 100);
    pwm.setPWM(i, 0, map(pos[i], 0, 100, servoPulseMin[i], servoPulseMax[i]));
  }
}
