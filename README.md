# Phantom

Developing an Arduino-Enabled Dynamic Ventricular Phantom for Evaluating Microvascular Lung Hydraulic Resistance

## Overview

Phantom is a real-time cardiovascular flow and pressure simulation system. It uses servo motors as variable-resistance valves and records data from flow and pressure sensors at 4 Hz. The system has two layers:

- **Arduino firmware** (`Phantom.ino`) -- controls 3 servos via an Adafruit PCA9685 I2C driver and reads 3 flow sensors + 3 pressure sensors.
- **Python interfaces** -- a graphical UI (`Phantom_GUI.py`) for live monitoring and a command-line UI (`Phantom_UI.py`) for quick manual control.

## Requirements

### Hardware

- **Arduino Uno**
  [Arduino Uno Rev3](https://store-usa.arduino.cc/products/arduino-uno-rev3?queryID=undefined&selectedStore=us)
- **Adafruit PCA9685 16-Channel Servo Driver** -- drives the servos from an external 7.4 V supply.
  [Adafruit PCA9685](https://www.adafruit.com/product/815)
- **3 Servo Motors** (FR5311M, 4.8-8.4 V, 13.8 kg-cm at 7.4 V) -- act as variable resistance valves (PV, CR1, CR2).
- **3 Flow Sensors** (YF-S401, 0.3-6 L/min, 5880 pulses/L) -- connected to digital pins D8, D7, D5.
- **3 Pressure Sensors** (0-10 PSI, 0.5-4.5 V output) -- connected to analog pins A0, A1, A2.
- **DC Power Supply** (7.4 V for the servo driver).

![image](https://github.com/Fredmichll/Phantom/assets/149977886/fe1bf998-b674-4a97-bbc9-5824daf53194)

**Figure 1: Arduino Hardware Configuration**

### Software

- **Arduino IDE** with the `Adafruit_PWMServoDriver` library.
- **Python 3.x** with `pyserial`, `matplotlib`, and `Pillow`.

## Installation

### Hydraulic Setup

- 1/4" tubing and Y fittings
- 1/4" female three-way tee joints and male-to-male straight hex adapters (for mounting pressure sensors)
- 2 Pulsatile Pumps P-120 (TRANDOMED) for left and right heart simulation.
  [Pulsatile Pump P-120](https://www.trando-med.com/pulsatile-pump/top-selling-pumps/pulsatile-pump-p-120-for-driving-vascular.html)

![image](https://github.com/Fredmichll/Phantom/assets/149977886/ca6718d9-69b5-4a1f-8225-fc4590b9d5d3)

**Figure 2: Hydraulic Configuration**

### Arduino Setup

1. Install the `Adafruit_PWMServoDriver` library in the Arduino IDE.
2. Connect the servos, flow sensors, and pressure sensors to their designated pins.
3. Open `Phantom.ino`, compile, and upload.

### Python Setup

```bash
pip install pyserial matplotlib Pillow
```

## Usage

### Graphical UI (recommended)

```bash
python Phantom_GUI.py
```

On launch a port-selection dialog lets you connect to the Arduino or run in **Demo Mode** (no hardware needed).

The GUI has three main areas:

| Area | Description |
|---|---|
| **Circuit panel** (left) | Displays the hydraulic design (`HydraulicDesign.png`) scaled to fit, with live sensor-value overlays. Click any sensor overlay to open a dedicated pop-up graph. |
| **Sidebar** (right) | Connection status, servo control (port selector, position slider, Send button, Set All Open/Closed), sensor pin configuration (reassign digital/analog pins at runtime), and session recording controls. |
| **Live graph** (bottom, collapsible) | Scrolling 20-second chart with separate flow (blue) and pressure (red) subplots. Updates at 4 Hz. |

#### Sensor polling

The UI polls the Arduino every **250 ms** (4 readings per second). All 6 sensor values (FL1-FL3, P1-P3) are updated on the circuit overlay and the live graph each cycle.

#### Session recording

1. Click **Start** in the Session section of the sidebar to begin recording.
2. Every poll cycle, sensor readings are buffered in memory.
3. Click **Stop**, then **Save** to export a timestamped CSV to the `data/` folder (e.g. `data/Session_2026-04-07_143022.csv`).

The CSV contains columns: `timestamp, fl1, fl2, fl3, p1, p2, p3`.

#### Servo control

- Select a PCA9685 **port** (0-15) and a **position** (200-350 ticks, where 200 = closed, 350 = open).
- Move the slider or type the value, then press **Send** (or Enter).
- **Set All Closed / Set All Open** sends the min/max position to all 16 channels at once.

### Command-Line UI

```bash
python Phantom_UI.py
```

Interactive menu:

1. **Get sensor readings** -- requests data from the Arduino and prints a formatted table. Results are appended to a timestamped text file.
2. **Update conditions** -- set servo openness percentages, pump rates, and fluid temperature. The Arduino adjusts servo positions accordingly.
3. **Beta run** -- test servo positions without affecting the main log file.
4. **Exit** -- close the connection.

### Calibration Sketches

- `Servo_calibration.ino` -- tune pulse lengths for specific servo angles.
- `Servo_functionality_test.ino` -- interactive diagnostics with I2C inspection and sweep tests.

## Project Structure

```
Phantom/
  Phantom.ino               # Arduino firmware
  PhantomController.py       # Shared serial controller class
  Phantom_UI.py              # Command-line interface
  Phantom_GUI.py             # GUI entry point
  HydraulicDesign.png        # Background image for the GUI
  data/                      # Session CSV output (git-ignored)
  UI/
    app.py                   # Main tkinter window
    circuit_panel.py         # Hydraulic diagram with sensor overlays
    control_panel.py         # Servo + pin config sidebar
    graph_panel.py           # Matplotlib live scrolling chart
    sensor_graph.py          # Per-sensor pop-up graph windows
    session.py               # CSV session recorder
    connection.py            # Port selection dialog
    constants.py             # Pins, colors, polling rate, paths
  Servo_calibration.ino      # Servo pulse-length calibration
  Servo_functionality_test.ino  # Servo diagnostics
  tests/
    test_servo_control.py    # Hardware integration tests
```

## Serial Protocol

| Direction | Message | Description |
|---|---|---|
| UI -> Arduino | `READ\n` | Request latest sensor data |
| Arduino -> UI | `fl1,fl2,fl3,p1,p2,p3\n` | CSV response (L/min, mmHg) |
| UI -> Arduino | `servo <port> <position>\n` | Move one servo (port 0-15, position 200-345 ticks) |
| UI -> Arduino | `SETPINS fl1,fl2,fl3,p1,p2,p3\n` | Reassign sensor pins at runtime |
| Arduino -> UI | `READY\n` | Sent once after startup init sweep completes |

## Troubleshooting

- **No ports detected** -- make sure the Arduino is connected via USB and the correct driver is installed. On macOS, look for `/dev/cu.usbmodem*`.
- **Sensor readings stuck at 0** -- verify physical wiring matches the pin assignments shown in the GUI sidebar. Use the pin-config dropdowns to reassign if needed.
- **Servo not moving** -- confirm the PCA9685 is powered (7.4 V external supply) and the I2C address is default (0x40). Run `Servo_functionality_test.ino` to diagnose.
- **Calibrating servos** -- use `Servo_calibration.ino` to find the exact pulse lengths for your servo model's 0% and 100% positions.

## License

This project is shared under the MIT License. See the [LICENSE](LICENSE) file for details.
