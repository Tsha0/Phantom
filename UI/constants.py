import os

# Project root directory (parent of UI/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Circuit diagram image path
CIRCUIT_IMAGE = os.path.join(PROJECT_ROOT, "CircuitDesign.png")

# Polling and graph settings
POLL_INTERVAL_MS = 2000
MAX_GRAPH_POINTS = 10  # 20 seconds at 2s intervals

# Default sensor pin assignments (user can change these in the UI)
DEFAULT_FLOW_PINS = {"fl1": "D8", "fl2": "D7", "fl3": "D5", "fl4": "D3"}
DEFAULT_PRESSURE_PINS = {"p1": "A0", "p2": "A1", "p3": "A2", "p4": "A3"}

# Available pins for assignment
DIGITAL_PINS = ["D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D13"]
ANALOG_PINS = ["A0", "A1", "A2", "A3", "A4", "A5"]

# Sensor overlay positions on CircuitDesign.png (x_fraction, y_fraction)
# Matched to the icons on the 4 horizontal paths in the diagram
SENSOR_POSITIONS = {
    "fl1": (0.33, 0.19),
    "fl2": (0.29, 0.42),
    "fl3": (0.42, 0.57),
    "fl4": (0.42, 0.72),
    "p1":  (0.50, 0.14),
    "p2":  (0.47, 0.38),
    "p3":  (0.55, 0.55),
    "p4":  (0.62, 0.70),
}

# Sensor units
SENSOR_UNITS = {
    "fl1": "L/min", "fl2": "L/min", "fl3": "L/min", "fl4": "L/min",
    "p1": "mmHg", "p2": "mmHg", "p3": "mmHg", "p4": "mmHg",
}

# Overlay colors on circuit diagram — single blue for flow, single red for pressure
OVERLAY_FLOW_COLOR = "#3b82f6"
OVERLAY_PRESSURE_COLOR = "#ef4444"

# Graph line colors — different shades so lines are distinguishable
SENSOR_COLORS = {
    "fl1": "#3b82f6", "fl2": "#60a5fa", "fl3": "#2563eb", "fl4": "#93c5fd",
    "p1":  "#ef4444", "p2":  "#f87171", "p3":  "#dc2626", "p4":  "#fca5a5",
}

# Valve/servo configuration — 4 valves (CR1-CR4), all 0-100%
VALVE_CONFIG = {
    "CR1": {
        "channel": 0,
        "pulse_range": (370, 520),
        "pct_min": 0,
        "pct_max": 100,
        "default": 50,
        "label": "CR1 [PWM Ch 0]",
    },
    "CR2": {
        "channel": 1,
        "pulse_range": (150, 290),
        "pct_min": 0,
        "pct_max": 100,
        "default": 50,
        "label": "CR2 [PWM Ch 1]",
    },
    "CR3": {
        "channel": 2,
        "pulse_range": (260, 410),
        "pct_min": 0,
        "pct_max": 100,
        "default": 50,
        "label": "CR3 [PWM Ch 2]",
    },
    "CR4": {
        "channel": 3,
        "pulse_range": (260, 410),
        "pct_min": 0,
        "pct_max": 100,
        "default": 50,
        "label": "CR4 [PWM Ch 3]",
    },
}

VALVE_NAMES = ["CR1", "CR2", "CR3", "CR4"]

# Sensor data keys in the order returned by Arduino CSV (4 flow + 4 pressure)
SENSOR_KEYS = ["fl1", "fl2", "fl3", "fl4", "p1", "p2", "p3", "p4"]

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
