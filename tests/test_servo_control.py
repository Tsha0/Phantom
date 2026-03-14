"""Hardware pytest to move Phantom servos via serial to Arduino.

Run with:
  ARDUINO_SERIAL=/dev/cu.usbmodemXXXX pytest -q tests/test_servo_control.py::test_move_servos

The test is skipped unless `ARDUINO_SERIAL` is set and `pyserial` is installed.
"""
from __future__ import annotations

import os
import time
import pytest

try:
    import serial
except Exception:
    serial = None


@pytest.fixture
def arduino_port():
    port = os.environ.get("ARDUINO_SERIAL") or os.environ.get("SERIAL_PORT")
    if not port:
        pytest.skip("No ARDUINO_SERIAL env var set; skipping hardware test")
    if serial is None:
        pytest.skip("pyserial not installed; install with `pip install pyserial`")
    return port


def test_move_servos(arduino_port):
    """Send a few servo position commands to the Arduino.

    The command format matches the UI: servo1,servo2,servo3,pump_left,pump_right,fluid_temp\n
    We only change the first three values (0-100 %). The test asserts bytes were written.
    """
    with serial.Serial(arduino_port, 9600, timeout=1) as ser:
        time.sleep(2)  # allow Arduino auto-reset / serial to settle

        positions = [
            (0, 0, 0),
            (50, 50, 50),
            (100, 0, 50),
        ]

        for s1, s2, s3 in positions:
            cmd = f"{int(s1)},{int(s2)},{int(s3)},0,0,0\n"
            written = ser.write(cmd.encode())
            assert written == len(cmd.encode()), f"wrote {written} bytes, expected {len(cmd.encode())}"
            ser.flush()
            time.sleep(1)  # allow servo to move
