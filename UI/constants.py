import os

# Project root directory (parent of UI/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Circuit diagram image path
CIRCUIT_IMAGE = os.path.join(PROJECT_ROOT, "HydraulicDesign.png")

# Data output directory
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# Polling and graph settings
POLL_INTERVAL_MS = 250   # 4 readings per second
MAX_GRAPH_POINTS = 80    # 20 seconds at 4Hz

# Default sensor pin assignments (user can change these in the UI)
DEFAULT_FLOW_PINS = {"fl1": "D8", "fl2": "D7", "fl3": "D5"}
DEFAULT_PRESSURE_PINS = {"p1": "A0", "p2": "A1", "p3": "A2"}

# Available pins for assignment
DIGITAL_PINS = ["D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D13"]
ANALOG_PINS = ["A0", "A1", "A2", "A3", "A4", "A5"]

# Sensor overlay positions on HydraulicDesign.png (x_fraction, y_fraction)
# Pulmonary path (top): FL1 leftmost, P1 rightmost (arrow gauge)
# PDA path (middle):    FL2 at tennis-ball icon, P2 to its right
# Systemic path (bottom): FL3 and P3
SENSOR_POSITIONS = {
    "fl1": (0.22, 0.18),
    "fl2": (0.35, 0.75),
    "fl3": (0.23, 0.99),
    "p1":  (0.78, 0.13),
    "p2":  (0.64, 0.72),
    "p3":  (0.75, 0.98),
}

# Sensor units
SENSOR_UNITS = {
    "fl1": "L/min", "fl2": "L/min", "fl3": "L/min",
    "p1": "mmHg", "p2": "mmHg", "p3": "mmHg",
}

# Overlay colors on circuit diagram — single blue for flow, single red for pressure
OVERLAY_FLOW_COLOR = "#3b82f6"
OVERLAY_PRESSURE_COLOR = "#ef4444"

# Graph line colors — different shades so lines are distinguishable
SENSOR_COLORS = {
    "fl1": "#3b82f6", "fl2": "#60a5fa", "fl3": "#2563eb",
    "p1":  "#ef4444", "p2":  "#f87171", "p3":  "#dc2626",
}

# Servo tick range (uniform for all servos on PCA9685)
SERVO_TICK_MIN = 200      # closed position
SERVO_TICK_MAX = 350      # open position
SERVO_TICK_DEFAULT = 200  # start closed (matches Arduino init)
SERVO_PORTS = list(range(16))  # PCA9685 channels 0-15

# Timeout for Arduino READY signal after init sweep
INIT_TIMEOUT_S = 10

# Sensor data keys in the order returned by Arduino CSV (3 flow + 3 pressure)
SENSOR_KEYS = ["fl1", "fl2", "fl3", "p1", "p2", "p3"]

# UI theme colors
BG_DARK = "#1e1e2e"
BG_PANEL = "#2a2a3d"
BG_CARD = "#353550"
FG_TEXT = "#e0e0e0"
FG_DIM = "#888899"
ACCENT_GREEN = "#4ade80"
ACCENT_RED = "#f87171"
ACCENT_BLUE = "#60a5fa"
ACCENT_PURPLE = "#a78bfa"
