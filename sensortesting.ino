// Pressure + flow sensor test
// Pressure: A0 only (5V supply, 0.5–4.5V -> 0–10 PSI)
// Flow: D2, D3, D8 pulse inputs (D8 uses a pin-change interrupt)
#include <PinChangeInterrupt.h>
const int PRESSURE_PIN = A0;
const float VCC = 5.0;
const float PSI_TO_MMHG = 51.715; // 1 PSI ≈ 51.715 mmHg

const int FLOW_PINS[] = {2, 3, 8};
volatile int flowCounts[] = {0, 0, 0};

void isrFlow0() { flowCounts[0]++; }
void isrFlow1() { flowCounts[1]++; }
void isrFlow2() { flowCounts[2]++; }

void setup() {
  Serial.begin(9600);
  while (!Serial) { ; }
  Serial.println("Pressure + flow sensor test (A0, D2/D3/D8)");

  pinMode(FLOW_PINS[0], INPUT_PULLUP);
  pinMode(FLOW_PINS[1], INPUT_PULLUP);
  pinMode(FLOW_PINS[2], INPUT_PULLUP);

  // D2 and D3 support external interrupts on Uno/Nano; D8 needs pin-change interrupt
  attachInterrupt(digitalPinToInterrupt(FLOW_PINS[0]), isrFlow0, RISING);
  attachInterrupt(digitalPinToInterrupt(FLOW_PINS[1]), isrFlow1, RISING);
  attachPCINT(digitalPinToPCINT(FLOW_PINS[2]), isrFlow2, RISING);
}

void loop() {
  unsigned long t_ms = millis();
  float t_s = t_ms / 1000.0;

  // Sensor on A0
  int raw0 = analogRead(PRESSURE_PIN);
  float voltage0 = raw0 * (VCC / 1023.0);
  float psi0;
  if (voltage0 <= 0.5) {
    psi0 = 0.0;
  } else if (voltage0 >= 4.5) {
    psi0 = 10.0;
  } else {
    psi0 = (voltage0 - 0.5) * 10.0 / 4.0; // span 4.0V from 0.5 to 4.5
  }
  float mmHg0 = psi0 * PSI_TO_MMHG;

  Serial.print("t(s):");
  Serial.println(t_s, 3);

  Serial.print("A0 Raw:");
  Serial.print(raw0);
  Serial.print(" V:");
  Serial.print(voltage0, 3);
  Serial.print(" PSI:");
  Serial.print(psi0, 2);
  Serial.print(" mmHg:");
  Serial.println(mmHg0, 1);

  // Capture flow counts over 1 second
  flowCounts[0] = flowCounts[1] = flowCounts[2] = 0;
  interrupts();
  delay(1000);
  noInterrupts();

  float flowLpm0 = flowCounts[0] / 98.0;
  float flowLpm1 = flowCounts[1] / 98.0;
  float flowLpm2 = flowCounts[2] / 98.0;

  Serial.print("Flow D2 (L/min): ");
  Serial.println(flowLpm0, 3);
  Serial.print("Flow D3 (L/min): ");
  Serial.println(flowLpm1, 3);
  Serial.print("Flow D8 (L/min): ");
  Serial.println(flowLpm2, 3);

  delay(1000); // overall cycle ~2s (1s flow window + 1s pause)
}