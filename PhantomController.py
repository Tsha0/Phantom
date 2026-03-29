import os
import random
import serial
import serial.tools.list_ports
import sys
import time
from datetime import datetime

def list_serial_ports():
    """List available serial ports."""
    ports = list(serial.tools.list_ports.comports())

    # Filter for common macOS Arduino port patterns
    arduino_ports = []
    other_ports = []

    for p in ports:
        device = p.device
        # Common Arduino patterns on macOS
        if any(pattern in device for pattern in ['usbmodem', 'usbserial', 'wchusbserial', 'SLAB']):
            arduino_ports.append(p)
        else:
            other_ports.append(p)

    return arduino_ports + other_ports

class PhantomController:
    """Controller class for the Phantom Arduino device."""

    def __init__(self, port=None, demo_mode=False):
        self.demo_mode = demo_mode
        self.port = port
        self.ser = None
        self.conditions = None

        if not demo_mode and port:
            try:
                self.ser = serial.Serial(port, 9600, timeout=1)
                time.sleep(2)  # Wait for Arduino to reset after serial connection
                self.wait_for_ready()
                print(f"Connected to {port}")
            except serial.SerialException as e:
                print(f"Error opening serial port: {e}")
                sys.exit(1)

    def wait_for_ready(self, timeout=10):
        """Block until Arduino sends 'READY' or timeout expires."""
        if self.demo_mode:
            return True

        start = time.time()
        buffer = ""
        while time.time() - start < timeout:
            if self.ser.in_waiting > 0:
                buffer += self.ser.read(self.ser.in_waiting).decode(errors='replace')
                if "READY" in buffer:
                    print("Arduino initialization complete")
                    return True
            time.sleep(0.1)

        print(f"Warning: Arduino READY not received within {timeout}s")
        return False

    def request_sensor_data(self):
        """Request and return sensor data from Arduino or generate mock data."""
        if self.demo_mode:
            flows = [round(random.uniform(0.5, 2.0), 2) for _ in range(4)]
            pressures = [round(random.uniform(5, 15) * 51.715, 1) for _ in range(4)]
            return ",".join(str(v) for v in flows + pressures)

        self.ser.write(b"READ\n")
        timeout_counter = 0
        while self.ser.in_waiting <= 0:
            time.sleep(0.1)
            timeout_counter += 1
            if timeout_counter > 50:  # 5 second timeout
                return "0,0,0,0,0,0,0,0"
        data = self.ser.readline().decode().strip()
        return data

    def send_servo_command(self, port, position):
        """Send a single servo command. Format: servo <port> <position>"""
        command = f"servo {port} {position}\n"

        if self.demo_mode:
            print(f"[Demo] {command.strip()}")
            return

        self.ser.write(command.encode())
        self.ser.flush()

    def close(self):
        """Close serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()
