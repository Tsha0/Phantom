#!/usr/bin/env python3
"""
Phantom UI for laptop

This script communicates with an Arduino device, sending commands to control
servo motors and reading back sensor data (flow and pressure). It supports:
- Cross-platform serial port selection (macOS /dev/cu.* and /dev/tty.* ports)
- Demo mode for testing without hardware
- Data logging to timestamped text files

Usage:
    python3 Phantom_UI_macOS.py

Requirements:
    pip3 install pyserial
"""
import serial
import serial.tools.list_ports
import time
import os
import sys
from datetime import datetime


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
                print(f"Connected to {port}")
            except serial.SerialException as e:
                print(f"Error opening serial port: {e}")
                sys.exit(1)

    def request_sensor_data(self):
        """Request and return sensor data from Arduino or generate mock data."""
        if self.demo_mode:
            # Generate plausible mock data
            import random
            flow1 = round(random.uniform(0.5, 2.0), 2)
            flow2 = round(random.uniform(0.5, 2.0), 2)
            flow3 = round(random.uniform(0.5, 2.0), 2)
            # Pressure in mmHg (PSI * 51.715)
            pressure1 = round(random.uniform(5, 15) * 51.715, 1)
            pressure2 = round(random.uniform(5, 15) * 51.715, 1)
            pressure3 = round(random.uniform(5, 15) * 51.715, 1)
            return f"{flow1},{flow2},{flow3},{pressure1},{pressure2},{pressure3}"

        self.ser.write(b"READ\n")
        timeout_counter = 0
        while self.ser.in_waiting <= 0:
            time.sleep(0.1)
            timeout_counter += 1
            if timeout_counter > 50:  # 5 second timeout
                return "0,0,0,0,0,0"
        data = self.ser.readline().decode().strip()
        return data

    def update_conditions(self, conditions):
        """Send new conditions to Arduino."""
        servo1, servo2, servo3, pump_left, pump_right, fluid_temp = conditions

        servo1 = int(servo1)
        servo2 = int(servo2)
        servo3 = int(servo3)

        command = f"{servo1},{servo2},{servo3},{pump_left},{pump_right},{fluid_temp}\n"

        if self.demo_mode:
            print(f"[Demo] Sending command: {command.strip()}")
            return

        self.ser.write(command.encode())
        self.ser.flush()
        time.sleep(1)

        # Read any response
        if self.ser.in_waiting > 0:
            response = self.ser.readline().decode().strip()
            if response:
                print(f"Arduino response: {response}")

    def close(self):
        """Close serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()


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


def select_port():
    """Interactive port selection."""
    print("\n" + "=" * 50)
    print("Phantom UI - Select Serial Port")
    print("=" * 50)

    ports = list_serial_ports()

    if not ports:
        print("\nNo serial ports detected.")
        print("Options:")
        print("  [d] Run in demo mode (no hardware required)")
        print("  [q] Quit")
        print()
        choice = input("Selection: ").strip().lower()
        if choice == 'd':
            return None, True  # Demo mode
        else:
            sys.exit(0)

    print("\nAvailable serial ports:")
    for idx, p in enumerate(ports):
        # Mark likely Arduino ports
        marker = " <-- likely Arduino" if 'usbmodem' in p.device or 'usbserial' in p.device else ""
        print(f"  [{idx}] {p.device}{marker}")
        if p.description and p.description != 'n/a':
            print(f"       {p.description}")

    print()
    print("  [d] Run in demo mode (no hardware)")
    print("  [q] Quit")
    print()

    choice = input("Select port number or option: ").strip().lower()

    if choice == 'q':
        sys.exit(0)
    elif choice == 'd':
        return None, True  # Demo mode
    elif choice.isdigit():
        idx = int(choice)
        if 0 <= idx < len(ports):
            return ports[idx].device, False
        else:
            print("Invalid selection.")
            sys.exit(1)
    else:
        print("Invalid selection.")
        sys.exit(1)


def collect_conditions():
    """Collect servo positions and other conditions from user."""
    prompts = [
        ("Servo PV position (10-100%)", 10, 100),
        ("Servo CR1 position (0-100%)", 0, 100),
        ("Servo CR2 position (10-100%)", 10, 100),
        ("Left pump rate (L/min)", 0, None),
        ("Right pump rate (L/min)", 0, None),
        ("Fluid temperature (°C)", 0, None),
    ]

    values = []
    for prompt, min_val, max_val in prompts:
        while True:
            try:
                user_input = input(f"{prompt}: ")
                value = float(user_input)

                if min_val is not None and value < min_val:
                    print(f"Error: Value must be at least {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    print(f"Error: Value must be at most {max_val}")
                    continue

                values.append(value)
                break
            except ValueError:
                print("Invalid input. Please enter a number.")

    return tuple(values)


def format_table(conditions, sensor_data=",,,,,", port="demo"):
    """Format conditions and sensor data into a readable table."""
    parts = sensor_data.split(',')
    if len(parts) != 6:
        parts = ['', '', '', '', '', '']

    flow1, flow2, flow3, pressure1, pressure2, pressure3 = parts
    servo1, servo2, servo3, pump_left, pump_right, fluid_temp = conditions
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    output = f"""
Timestamp: {timestamp}
Port: {port}
{'=' * 50}
Output Name                  | Reading
-----------------------------|------------------
Servo PV Openness (%)        | {servo1}
Servo CR1 Openness (%)       | {servo2}
Servo CR2 Openness (%)       | {servo3}
Left Pump Rate (L/min)       | {pump_left}
Right Pump Rate (L/min)      | {pump_right}
Fluid Temperature (°C)       | {fluid_temp}
-----------------------------|------------------
FL1 Flow Rate (L/min)        | {flow1}
FL2 Flow Rate (L/min)        | {flow2}
FL3 Flow Rate (L/min)        | {flow3}
P1 Pressure (mmHg)           | {pressure1}
P2 Pressure (mmHg)           | {pressure2}
P3 Pressure (mmHg)           | {pressure3}
{'=' * 50}
"""
    return output


def get_output_filename(prefix="Output"):
    """Generate a timestamped output filename in the script's directory."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return os.path.join(script_dir, f"{prefix}_{timestamp}.txt")


def main():
    # Select port or demo mode
    port, demo_mode = select_port()

    mode_str = "Demo Mode" if demo_mode else f"Connected to {port}"
    print(f"\n{mode_str}")
    print("-" * 50)

    # Initialize controller
    controller = PhantomController(port=port, demo_mode=demo_mode)

    # Collect initial conditions
    print("\nEnter initial conditions:")
    conditions = collect_conditions()
    controller.update_conditions(conditions)
    controller.conditions = conditions

    # Setup output file
    output_file = get_output_filename()
    print(f"\nLogging to: {output_file}")

    # Main loop
    while True:
        print("\n" + "-" * 30)
        print("1. Get sensor readings")
        print("2. Update conditions")
        print("3. Beta run (test without logging)")
        print("4. Exit")
        print("-" * 30)

        choice = input("Select option: ").strip()

        if choice == '1':
            sensor_data = controller.request_sensor_data()
            output = format_table(conditions, sensor_data, port or "demo")
            print(output)

            with open(output_file, "a") as f:
                f.write(output + "\n")
            print(f"Data logged to {output_file}")

        elif choice == '2':
            print("\nEnter new conditions:")
            conditions = collect_conditions()
            controller.update_conditions(conditions)
            controller.conditions = conditions

            output = format_table(conditions, ",,,,,", port or "demo")
            with open(output_file, "a") as f:
                f.write(output + "\n")
            print("Conditions updated and logged.")

        elif choice == '3':
            print("\n[Beta Run] Testing servo positions...")
            controller.update_conditions(conditions)
            output = format_table(conditions, "-,-,-,-,-,-", port or "demo")
            print(output)

            # Log to separate beta file
            beta_file = get_output_filename("Beta")
            with open(beta_file, "a") as f:
                f.write(output + "\n")
            print(f"Beta data logged to {beta_file}")

        elif choice == '4':
            print("\nExiting...")
            controller.close()
            break

        else:
            print("Invalid option. Please enter 1-4.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Exiting...")
        sys.exit(0)
