# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Phantom is an Arduino-based Dynamic Ventricular Phantom that simulates cardiovascular flow and pressure conditions. It uses servo motors as variable resistance valves and records data from flow/pressure sensors. The system has two layers: Arduino firmware for hardware control and a Python UI for operator interaction over serial.

## Architecture

**Firmware (Arduino C++):** `Phantom.ino` runs on an Arduino Uno with an Adafruit PCA9685 I2C servo driver. It controls 3 servos (PV, CR1, CR2) and reads 3 flow sensors (interrupt-driven pulse counting) and 3 pressure sensors (analog ADC). Communication with the Python UI uses a CSV-based serial protocol.

**Python CLI:** `Phantom_UI.py` provides a `PhantomController` class for serial communication and a CLI menu interface. Supports cross-platform port selection, demo mode (no hardware needed), and data logging.

**Python GUI:** `UI/` package (tkinter + matplotlib). Displays the circuit diagram (`circuit.png`) with live sensor overlays, valve sliders, real-time graphs, and session recording to CSV. Run via `python run_gui.py`. Modules: `app.py` (main window), `circuit_panel.py`, `control_panel.py`, `graph_panel.py`, `session.py`, `connection.py` (imports `PhantomController` from `Phantom_UI.py`), `constants.py`.

**Serial Protocol:**
- UI sends: `servo1%,servo2%,servo3%,pump_left,pump_right,temp`
- Arduino responds to `READ` command with: `flow1,flow2,flow3,pressure1,pressure2,pressure3`

**Calibration sketches:** `Servo_calibration.ino` (pulse length tuning), `Servo_functionality_test.ino` (interactive diagnostics with I2C inspection and sweep tests).

## Build and Run

**Firmware:** Open `.ino` files in Arduino IDE, compile, and upload. Requires the `Adafruit_PWMServoDriver.h` library.

**Python CLI:**
```bash
pip install pyserial
python Phantom_UI.py
```

**Python GUI:**
```bash
pip install pyserial matplotlib
python run_gui.py
```

**Tests:**
```bash
pip install pyserial pytest
ARDUINO_SERIAL=/dev/cu.usbmodemXXXX pytest -q tests/test_servo_control.py
```
Tests require a connected Arduino; set `ARDUINO_SERIAL` to the device's serial port.

## Hardware Constraints

- Servo PV and CR2: 10-100% openness only
- Servo CR1: 0-100% openness
- Flow sensors: YF-S401, 5880 pulses/L conversion factor
- Pressure sensors: 0-10 PSI range, 0.5-4.5V output
