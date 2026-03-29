#include <Adafruit_PWMServoDriver.h>

// Create the Adafruit_PWMServoDriver object, using the default I2C address 0x40
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

// Define the PWM channels that the servos are connected to on the Adafruit PWM Servo Driver
#define SERVO1_PWM_CHANNEL 0 // Connected to channel 0
#define SERVO2_PWM_CHANNEL 1 // Connected to channel 1
#define SERVO3_PWM_CHANNEL 2 // Connected to channel 2

void setup() {
  Serial.begin(9600);
  pwm.begin(); // Initialize the PWM driver
  pwm.setPWMFreq(60); // Set the PWM frequency to 60 Hz (common for servos)
  
  // No need to attach servos as we are controlling them through the Adafruit PWM Servo Driver
}

void loop() {
  // Example positions to test each servo
  // You might need to adjust the min and max pulse lengths (150 to 600) based on your servos' specifics

  /*
  First part of the calibration
  */
  
  pwm.setPWM(SERVO1_PWM_CHANNEL, 0, 370); // for PV (370) is 0 and (520) is 90
  pwm.setPWM(SERVO2_PWM_CHANNEL, 0, 290); // for CR1 (150) is 0 and (290) is 90
  pwm.setPWM(SERVO3_PWM_CHANNEL, 0, 410); // for CR2 (260) is 0 and (410) is 90

  /*
  Second part of the calibration to test map from % to PWM pulse length count
  When you are done with the first part, comment line 27 to 29 and uncomment lines 36 to 38, 41 to 43, 46 to 48
  */
  
  //int servo1Pos = 5; // Example percentage for servo1
  //int servo2Pos = 0; // Example percentage for servo2
  //int servo3Pos = 0; // Example percentage for servo3
  
  // Map the percentage positions to pulse lengths
  //int servo1Pulse = map(servo1Pos, 0, 100, 370, 520); // Adjust these values for your servo
  //int servo2Pulse = map(servo2Pos, 0, 100, 150, 290); // Adjust these values for your servo
  //int servo3Pulse = map(servo3Pos, 0, 100, 260, 410); // Adjust these values for your servo

  // Use the PWM driver to set the servo positions
  //pwm.setPWM(SERVO1_PWM_CHANNEL, 0, servo1Pulse);
  //pwm.setPWM(SERVO2_PWM_CHANNEL, 0, servo2Pulse);
  //pwm.setPWM(SERVO3_PWM_CHANNEL, 0, servo3Pulse);

  delay(1000); // Wait 1 second
}
