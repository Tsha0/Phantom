#include <Adafruit_PWMServoDriver.h>
#include <Wire.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

const int SERVO_COUNT = 3;
const uint8_t SERVO_CHANNELS[SERVO_COUNT] = {0, 2, 3};
const int SERVO_MIN_PULSE[SERVO_COUNT] = {370, 150, 260}; // PV, CR1, CR2
const int SERVO_MAX_PULSE[SERVO_COUNT] = {520, 290, 410}; // PV, CR1, CR2
const char* SERVO_NAMES[SERVO_COUNT] = {"PV", "CR1", "CR2"};

const int TEST_POINTS[] = {0, 25, 50, 75, 100, 50, 0};
const int TEST_POINT_COUNT = sizeof(TEST_POINTS) / sizeof(TEST_POINTS[0]);

const uint8_t PCA9685_ADDR = 0x40;

uint8_t readPcaRegister(uint8_t reg) {
  Wire.beginTransmission(PCA9685_ADDR);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) {
    return 0xFF;
  }

  Wire.requestFrom(PCA9685_ADDR, (uint8_t)1);
  if (Wire.available()) {
    return Wire.read();
  }
  return 0xFE;
}

void dumpPcaStatus() {
  uint8_t mode1 = readPcaRegister(0x00);
  uint8_t mode2 = readPcaRegister(0x01);
  uint8_t prescale = readPcaRegister(0xFE);

  Serial.println("PCA9685 registers:");
  Serial.print("  MODE1: 0x");
  Serial.println(mode1, HEX);
  Serial.print("  MODE2: 0x");
  Serial.println(mode2, HEX);
  Serial.print("  PRESCALE: 0x");
  Serial.println(prescale, HEX);
}

void dumpChannelRegisters(uint8_t channel) {
  uint8_t base = 0x06 + (4 * channel);
  uint8_t onL = readPcaRegister(base + 0);
  uint8_t onH = readPcaRegister(base + 1);
  uint8_t offL = readPcaRegister(base + 2);
  uint8_t offH = readPcaRegister(base + 3);

  Serial.print("  CH ");
  Serial.print(channel);
  Serial.print(" ON=");
  Serial.print((int)(onH << 8 | onL));
  Serial.print(" OFF=");
  Serial.println((int)(offH << 8 | offL));
}

void runDiagnostics() {
  Serial.println("\n=== PCA9685 Diagnostics ===");
  dumpPcaStatus();
  Serial.println("Mapped channels:");
  dumpChannelRegisters(SERVO_CHANNELS[0]);
  dumpChannelRegisters(SERVO_CHANNELS[1]);
  dumpChannelRegisters(SERVO_CHANNELS[2]);
  Serial.println();
}

void scanI2CBus() {
  Serial.println("Scanning I2C bus...");
  int foundCount = 0;
  bool foundPCA = false;

  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    uint8_t error = Wire.endTransmission();

    if (error == 0) {
      Serial.print("I2C device found at 0x");
      if (addr < 16) {
        Serial.print('0');
      }
      Serial.println(addr, HEX);
      foundCount++;
      if (addr == 0x40) {
        foundPCA = true;
      }
    }
  }

  if (foundCount == 0) {
    Serial.println("No I2C devices found.");
  }

  if (foundPCA) {
    Serial.println("PCA9685 detected at 0x40.");
  } else {
    Serial.println("PCA9685 NOT detected at 0x40.");
    Serial.println("Check SDA/SCL, GND, and board power.");
  }
  Serial.println();
}

void printHelp() {
  Serial.println();
  Serial.println("=== Servo Functionality Test (PCA9685) ===");
  Serial.println("Commands:");
  Serial.println("  HELP             -> Show this message");
  Serial.println("  DIAG             -> Dump PCA9685 register diagnostics");
  Serial.println("  TEST             -> Run automatic sweep test on all 3 servos");
  Serial.println("  SET n p          -> Move servo n (1-3) to p% (0-100)");
  Serial.println("  RAW n pulse      -> Move servo n with raw pulse count (100-650)");
  Serial.println("  WIDE n           -> Wide raw sweep test for servo n (1-3)");
  Serial.println("  ALL p1 p2 p3     -> Set all 3 servos by percent (0-100)");
  Serial.println("  CENTER           -> Set all servos to 50%");
  Serial.println("  ZERO             -> Set all servos to 0%");
  Serial.println();
}

int percentToPulse(int servoIndex, int percent) {
  percent = constrain(percent, 0, 100);
  return map(percent, 0, 100, SERVO_MIN_PULSE[servoIndex], SERVO_MAX_PULSE[servoIndex]);
}

void setServoPercent(int servoIndex, int percent) {
  int clamped = constrain(percent, 0, 100);
  int pulse = percentToPulse(servoIndex, clamped);
  pwm.setPWM(SERVO_CHANNELS[servoIndex], 0, pulse);

  Serial.print("Servo ");
  Serial.print(SERVO_NAMES[servoIndex]);
  Serial.print(" (ch ");
  Serial.print(SERVO_CHANNELS[servoIndex]);
  Serial.print(") -> ");
  Serial.print(clamped);
  Serial.print("% (pulse ");
  Serial.print(pulse);
  Serial.println(")");
}

void setServoRawPulse(int servoIndex, int pulse) {
  int clamped = constrain(pulse, 100, 650);
  pwm.setPWM(SERVO_CHANNELS[servoIndex], 0, clamped);

  Serial.print("Servo ");
  Serial.print(SERVO_NAMES[servoIndex]);
  Serial.print(" (ch ");
  Serial.print(SERVO_CHANNELS[servoIndex]);
  Serial.print(") -> RAW pulse ");
  Serial.println(clamped);
}

void setAllServos(int p1, int p2, int p3) {
  setServoPercent(0, p1);
  setServoPercent(1, p2);
  setServoPercent(2, p3);
}

void runAutomaticTest() {
  Serial.println("\nStarting automatic sweep test...");

  for (int servo = 0; servo < SERVO_COUNT; servo++) {
    Serial.print("\nTesting servo ");
    Serial.println(SERVO_NAMES[servo]);

    for (int i = 0; i < TEST_POINT_COUNT; i++) {
      setServoPercent(servo, TEST_POINTS[i]);
      delay(700);
    }
  }

  Serial.println("\nAutomatic test complete. Setting all servos to 0%.");
  setAllServos(0, 0, 0);
}

void runWideRangeTest(int servoIndex) {
  const int rawPoints[] = {120, 220, 320, 420, 520, 620, 420, 220, 120};
  const int count = sizeof(rawPoints) / sizeof(rawPoints[0]);

  Serial.print("\nWide raw sweep for servo ");
  Serial.println(SERVO_NAMES[servoIndex]);

  for (int i = 0; i < count; i++) {
    setServoRawPulse(servoIndex, rawPoints[i]);
    delay(700);
  }
}

void handleSerialCommand(String cmd) {
  cmd.trim();
  if (cmd.length() == 0) {
    return;
  }

  if (cmd.equalsIgnoreCase("HELP")) {
    printHelp();
    return;
  }

  if (cmd.equalsIgnoreCase("DIAG")) {
    runDiagnostics();
    return;
  }

  if (cmd.equalsIgnoreCase("TEST")) {
    runAutomaticTest();
    return;
  }

  if (cmd.equalsIgnoreCase("CENTER")) {
    setAllServos(50, 50, 50);
    return;
  }

  if (cmd.equalsIgnoreCase("ZERO")) {
    setAllServos(0, 0, 0);
    return;
  }

  int n, p;
  if (sscanf(cmd.c_str(), "SET %d %d", &n, &p) == 2) {
    if (n < 1 || n > 3) {
      Serial.println("Error: servo index must be 1, 2, or 3.");
      return;
    }
    setServoPercent(n - 1, p);
    return;
  }

  int rawServo, rawPulse;
  if (sscanf(cmd.c_str(), "RAW %d %d", &rawServo, &rawPulse) == 2) {
    if (rawServo < 1 || rawServo > 3) {
      Serial.println("Error: servo index must be 1, 2, or 3.");
      return;
    }
    setServoRawPulse(rawServo - 1, rawPulse);
    return;
  }

  int wideServo;
  if (sscanf(cmd.c_str(), "WIDE %d", &wideServo) == 1) {
    if (wideServo < 1 || wideServo > 3) {
      Serial.println("Error: servo index must be 1, 2, or 3.");
      return;
    }
    runWideRangeTest(wideServo - 1);
    return;
  }

  int p1, p2, p3;
  if (sscanf(cmd.c_str(), "ALL %d %d %d", &p1, &p2, &p3) == 3) {
    setAllServos(p1, p2, p3);
    return;
  }

  Serial.print("Unknown command: ");
  Serial.println(cmd);
  printHelp();
}

void setup() {
  Serial.begin(9600);
  Wire.begin();
  scanI2CBus();
  pwm.begin();
  pwm.setPWMFreq(60);

  delay(200);
  setAllServos(0, 0, 0);
  runDiagnostics();

  printHelp();
  Serial.println("Type a command and press Enter.");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    handleSerialCommand(command);
  }
}
