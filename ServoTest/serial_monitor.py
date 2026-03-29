#!/usr/bin/env python3
"""
ServoTest/serial_monitor.py
Simple serial monitor to watch Arduino output from any of the ServoTest sketches.

Usage:
    source ../.venv/bin/activate
    python3 ServoTest/serial_monitor.py

Or specify a port:
    python3 ServoTest/serial_monitor.py /dev/cu.usbmodem1101
"""

import sys
import serial
import serial.tools.list_ports

PORT = "/dev/cu.usbmodem1101"
BAUD = 9600

def pick_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found.")
        sys.exit(1)

    if len(ports) == 1:
        return ports[0].device

    print("Available ports:")
    for i, p in enumerate(ports):
        print(f"  {i+1}) {p.device} - {p.description}")
    idx = int(input("Select port number: ")) - 1
    return ports[idx].device

if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else PORT

    try:
        ser = serial.Serial(port, BAUD, timeout=1)
        print(f"Connected to {port} at {BAUD} baud. Ctrl+C to quit.\n")
        while True:
            line = ser.readline().decode("utf-8", errors="replace").rstrip()
            if line:
                print(line)
    except serial.SerialException as e:
        print(f"Could not open {port}: {e}")
        print("Available ports:")
        for p in serial.tools.list_ports.comports():
            print(f"  {p.device} - {p.description}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nDisconnected.")
