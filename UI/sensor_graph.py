import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .constants import (
    MAX_GRAPH_POINTS, SENSOR_COLORS, SENSOR_UNITS, BG_DARK,
    DEFAULT_FLOW_PINS, DEFAULT_PRESSURE_PINS,
)


class SensorGraphWindow(tk.Toplevel):
    """Popup window showing a live line graph for a single sensor (past 20s)."""

    _open_windows = {}

    @classmethod
    def open_for(cls, parent, sensor_key):
        if sensor_key in cls._open_windows:
            win = cls._open_windows[sensor_key]
            try:
                win.lift()
                win.focus_force()
                return win
            except tk.TclError:
                del cls._open_windows[sensor_key]

        win = cls(parent, sensor_key)
        cls._open_windows[sensor_key] = win
        return win

    def __init__(self, parent, sensor_key):
        super().__init__(parent)
        self._key = sensor_key

        all_pins = {**DEFAULT_FLOW_PINS, **DEFAULT_PRESSURE_PINS}
        pin = all_pins.get(sensor_key, "?")
        self._label = f"{sensor_key.upper()} [{pin}]"
        self._unit = SENSOR_UNITS.get(sensor_key, "")
        color = SENSOR_COLORS.get(sensor_key, "#60a5fa")

        self.title(f"{self._label} \u2014 Live Graph")
        self.geometry("600x350")
        self.configure(bg=BG_DARK)

        self._timestamps = []
        self._values = []

        self.fig, self.ax = plt.subplots(figsize=(6, 3), dpi=90)
        self.fig.patch.set_facecolor("#1e1e2e")
        self.ax.set_facecolor("#2a2a3d")
        self.ax.tick_params(colors="#aaaaaa")
        self.ax.spines["bottom"].set_color("#555555")
        self.ax.spines["left"].set_color("#555555")
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.set_ylabel(self._unit, color="#cccccc", fontsize=10)
        self.ax.set_xlabel("Time (s)", color="#cccccc", fontsize=10)
        self.ax.set_title(f"{self._label} \u2014 Past 20s", color="#e0e0e0",
                          fontsize=12, fontweight="bold")
        self.ax.grid(True, alpha=0.2, color="#666666")

        (self._line,) = self.ax.plot([], [], color=color, linewidth=2)
        self.fig.tight_layout(pad=1.5)

        self._canvas = FigureCanvasTkAgg(self.fig, master=self)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def update_data(self, value: float, elapsed: float):
        self._timestamps.append(elapsed)
        self._values.append(value)

        if len(self._timestamps) > MAX_GRAPH_POINTS:
            excess = len(self._timestamps) - MAX_GRAPH_POINTS
            self._timestamps = self._timestamps[excess:]
            self._values = self._values[excess:]

        self._line.set_data(self._timestamps, self._values)
        self.ax.relim()
        self.ax.autoscale_view()
        self._canvas.draw_idle()

    def _on_close(self):
        self._open_windows.pop(self._key, None)
        plt.close(self.fig)
        self.destroy()
