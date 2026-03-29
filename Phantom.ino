/*
  Phantom — Dynamic Ventricular Phantom firmware

  Servo motors (PCA9685 I2C PWM driver, channels 0-15):
    CR1 (ch 0)    CR2 (ch 1)    CR3 (ch 2)    CR4 (ch 3)

  Flow sensors (digital interrupt, YF-S401 — 5880 pulses/L):
    FL1 — pin 8    FL2 — pin 7    FL3 — pin 5    FL4 — pin 3

  Pressure sensors (analog, 0-10 PSI, 0.5-4.5 V output):
    P1 — A0    P2 — A1    P3 — A2    P4 — A3

  Serial protocol:
    RX  "READ\n"                        → TX sensor CSV
    RX  "servo <port> <position>\n"     → move one servo (port 0-15, position 200-345 ticks)
    TX  "fl1,fl2,fl3,fl4,p1,p2,p3,p4\n"→ CSV in L/min and mmHg
    TX  "READY\n"                       → sent once after init sweep completes
*/

#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Servo tick range (uniform for all servos)
const int SERVO_CLOSE = 200;
const int SERVO_OPEN  = 345;

// Non-blocking gradual movement state (16 PCA9685 channels)
int currentPos[16];
int targetPos[16];
unsigned long lastStepTime[16];
const unsigned long STEP_INTERVAL_MS = 10;

const int flowSensorPins[] = {8, 7, 5, 3};
const int pressureSensorPins[] = {A0, A1, A2, A3};

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

  // Initialize all channel tracking to closed position
  for (int i = 0; i < 16; i++) {
    currentPos[i] = SERVO_CLOSE;
    targetPos[i]  = SERVO_CLOSE;
    lastStepTime[i] = 0;
  }

  // Initialization sweep: close -> open -> close on channels 0-3
  for (int tick = SERVO_CLOSE; tick <= SERVO_OPEN; tick++) {
    for (int i = 0; i < 4; i++) {
      pwm.setPWM(i, 0, tick);
    }
    delay(10);
  }
  for (int tick = SERVO_OPEN; tick >= SERVO_CLOSE; tick--) {
    for (int i = 0; i < 4; i++) {
      pwm.setPWM(i, 0, tick);
    }
    delay(10);
  }

  // All servos now at SERVO_CLOSE
  for (int i = 0; i < 4; i++) {
    currentPos[i] = SERVO_CLOSE;
    targetPos[i]  = SERVO_CLOSE;
  }

  Serial.println("READY");
}

void loop() {
  // Process incoming serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command == "READ") {
      readAndSendSensorData();
    } else if (command.startsWith("servo ")) {
      parseServoCommand(command);
    }
  }

  // Non-blocking gradual servo movement
  unsigned long now = millis();
  for (int i = 0; i < 16; i++) {
    if (currentPos[i] != targetPos[i] && (now - lastStepTime[i] >= STEP_INTERVAL_MS)) {
      if (currentPos[i] < targetPos[i]) {
        currentPos[i]++;
      } else {
        currentPos[i]--;
      }
      pwm.setPWM(i, 0, currentPos[i]);
      lastStepTime[i] = now;
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

void parseServoCommand(String command) {
  // Format: "servo <port> <position>"
  int firstSpace = command.indexOf(' ', 6);
  if (firstSpace == -1) return;

  int port = command.substring(6, firstSpace).toInt();
  int position = command.substring(firstSpace + 1).toInt();

  if (port < 0 || port > 15) return;
  position = constrain(position, SERVO_CLOSE, SERVO_OPEN);

  targetPos[port] = position;
}
