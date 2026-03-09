/*
  Variables and objects initialization 
  The servo motors are connected PWM pins
  servo1 (PV) simulates variations in PVR 
  servo2 (CR1) simulates constant resistance in the pulmonary pathway
  servo3 (CR2) simulates constant resistance in the systemic pathway

  The pressure sensors are connected to digital pins
  Pressure Sensor 1 (P1) is connected to A0 (Pin A1)
  Pressure Sensor 2 (P2) is connected to A1 (Pin A2)
  Pressure Sensor 3 (P3) is connected to A2 (Pin A3)
  
  The flow sensors are connected to analog pins
  Flow Sensor 1 (FL1) is connected to D7 (Pin 8)
  Flow Sensor 2 (FL2) is connected to D6 (Pin 7)
  Flow Sensor 3 (FL3) is connected to D4 (Pin 5)
*/

#include <Adafruit_PWMServoDriver.h>

// Initialize the PWM driver. By default, it uses I2C address 0x40.
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Define the PWM channels for the servo motors
#define SERVO1_PWM 0 // PV
#define SERVO2_PWM 1 // CR1
#define SERVO3_PWM 2 // CR2

// Define the flow and pressure sensor pins
const int flowSensorPins[] = {8, 7, 5};
const int pressureSensorPins[] = {A1, A2, A3};

// Initialize Global pulse counters for the flow sensors
volatile int pulseCountFL1 = 0; // {FL1,FL2,FL3}
volatile int pulseCountFL2 = 0; // {FL1,FL2,FL3}
volatile int pulseCountFL3 = 0; // {FL1,FL2,FL3}

void pulseCounterFL1() {pulseCountFL1++; }
void pulseCounterFL2() {pulseCountFL2++; }
void pulseCounterFL3() {pulseCountFL3++; }

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  pwm.begin();

  pwm.setPWMFreq(60);  // Servos typically run at 50-60 Hz
  
  // Initialize the flow sensor pins as inputs
  pinMode(flowSensorPins[0], INPUT_PULLUP);
  pinMode(flowSensorPins[1], INPUT_PULLUP);
  pinMode(flowSensorPins[2], INPUT_PULLUP);

  
  // Attach the interrupt service routines for the flow sensors
  attachInterrupt(digitalPinToInterrupt(flowSensorPins[0]), pulseCounterFL1, RISING);
  attachInterrupt(digitalPinToInterrupt(flowSensorPins[1]), pulseCounterFL2, RISING);
  attachInterrupt(digitalPinToInterrupt(flowSensorPins[2]), pulseCounterFL3, RISING);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    if (command == "READ") {
      readAndSendSensorData();
    } else {
      adjustServosAndConditions(command);
    }
  }
}

void readAndSendSensorData() {
  // Reset pulse counters
  pulseCountFL1 = 0;
  pulseCountFL2 = 0;
  pulseCountFL3 = 0;
  
  // Start the measurement period of 1 sec to calculate flow rates
  interrupts();
  delay(1000);
  noInterrupts();

  float flow1 = readFlowSensor(pulseCountFL1);
  float flow2 = readFlowSensor(pulseCountFL2);
  float flow3 = readFlowSensor(pulseCountFL3);
  float pressure1 = readPressureSensor(pressureSensorPins[0]);
  float pressure2 = readPressureSensor(pressureSensorPins[1]);
  float pressure3 = readPressureSensor(pressureSensorPins[2]);

  // Validate and correct flow rates
  flow1 = (flow1 >= 0) ? flow1 : 0;
  flow2 = (flow2 >= 0) ? flow2 : 0;
  flow3 = (flow3 >= 0) ? flow3 : 0;

  // Validate and correct pressure values
  pressure1 = (pressure1 >= 0) ? pressure1 : 0;
  pressure2 = (pressure2 >= 0) ? pressure2 : 0;
  pressure3 = (pressure3 >= 0) ? pressure3 : 0;

  // Send the data over Serial
  Serial.println(String(flow1) + "," + String(flow2) + "," + String(flow3) + "," + String(pressure1) + "," + String(pressure2) + "," + String(pressure3));

}

  /*
  The readFlowSensor will convert the frequency readings to Flow Rates to L/min.
  For the SEN0216 Digital Water Flow Sensor 1L = 5880 pulses, thus the equation
  x = number of pulses recorded by flow sensor
  for the flow rate is Q = x/5880 (L/s) which gives Q = x/98 (L/min)
  */

float readFlowSensor(int pulseCount) {
  // Read and record the sensors readings 
  return pulseCount/98.0;
} 

float readPressureSensor(int pin) {
  const float Vcc = 5.0; // Power supply voltage
  const float psi_to_mmHg = 51.715; // Conversion factor from PSI to mmHg 
  int sensorValue = analogRead(pin); // Read the sensor value
  float voltage = sensorValue * (Vcc / 1023.0); // Convert the value to voltage

  // Assuming a 0.5-4.5V output range for 0-30 PSI


  /*
  ****************************************************************************
  potential problem here

  The pressure sensors you're using output 0–10 PSI (according to the README specs), 
  but the Arduino code is calibrated to interpret the voltage range as 0–30 PSI.
  
  */
  float psi;
  if (voltage <= 0.5) {
    psi = 0.0; // Handle error condition or below range
  } else if (voltage >= 4.5) {
    psi = 30.0; // Handle error condition or above range
  } else {
    psi = (voltage - 0.5) * 30.0 / (4.5 - 0.5); // Map voltage to PSI
  }

  return psi * psi_to_mmHg; // Convert PSI to mmHg and return
}

void adjustServosAndConditions(String conditions) {

  // Parse the conditions string
  int firstComma = conditions.indexOf(',');
  int secondComma = conditions.indexOf(',', firstComma + 1);
  int thirdComma = conditions.indexOf(',', secondComma + 1);

  // Assuming the string format is: servo1,servo2,servo3,*,*,*,*,*
  int servo1Pos = conditions.substring(0, firstComma).toInt();
  int servo2Pos = conditions.substring(firstComma + 1, secondComma).toInt();
  int servo3Pos = conditions.substring(secondComma + 1, thirdComma).toInt();

  // Convert percentage to servo angle (0-100% -> 0-90 degrees)
  // Each servo motors have their own pulselength values to reach angles between 0 and 90 degrees
  // Map from % to PWM pulse length count
  pwm.setPWM(SERVO1_PWM, 0, map(servo1Pos, 0, 100, 370, 520)); // for PV : 370 count equals an angle of 0 and a 520 count is an angle of 90
  pwm.setPWM(SERVO2_PWM, 0, map(servo2Pos, 0, 100, 150, 290)); // for CR1 : 150 count equals an angle of 0 and a 290 count is an angle of 90
  pwm.setPWM(SERVO3_PWM, 0, map(servo3Pos, 0, 100, 260, 410)); // for CR2 : 260 count equals an angle of 0 and a 410 count is an angle of 90
}
