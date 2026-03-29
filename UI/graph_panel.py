import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .constants import MAX_GRAPH_POINTS, SENSOR_COLORS, SENSOR_KEYS, BG_DARK

FLOW_KEYS = [k for k in SENSOR_KEYS if k.startswith("fl")]
PRESSURE_KEYS = [k for k in SENSOR_KEYS if k.startswith("p")]

PIN_LABELS = {
    "fl1": "D8", "fl2": "D7", "fl3": "D5", "fl4": "D3",
    "p1": "A0", "p2": "A1", "p3": "A2", "p4": "A3",
}


class GraphPanel(tk.Frame):
    """Live scrolling chart — past 20 seconds of flow (blue) and pressure (red)."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self._timestamps = []
        self._data = {k: [] for k in SENSOR_KEYS}
        self._build()

    def _build(self):
        self.fig, (self.ax_flow, self.ax_pressure) = plt.subplots(
            2, 1, sharex=True, figsize=(10, 4), dpi=80,
        )
        self.fig.patch.set_facecolor("#1e1e2e")
        self.fig.subplots_adjust(hspace=0.35, left=0.07, right=0.96, top=0.92, bottom=0.12)

        for ax in (self.ax_flow, self.ax_pressure):
            ax.set_facecolor("#2a2a3d")
            ax.tick_params(colors="#aaaaaa", labelsize=8)
            ax.spines["bottom"].set_color("#555555")
            ax.spines["left"].set_color("#555555")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.grid(True, alpha=0.2, color="#666666")

        # Flow subplot (all blue shades)
        self.ax_flow.set_ylabel("Flow (L/min)", color="#cccccc", fontsize=9)
        self.ax_flow.set_title("Live Sensor Data — Past 20s", fontsize=10,
                               color="#e0e0e0", fontweight="bold")
        self._flow_lines = {}
        for key in FLOW_KEYS:
            label = f"{key.upper()} [{PIN_LABELS[key]}]"
            (line,) = self.ax_flow.plot(
                [], [], color=SENSOR_COLORS[key], label=label, linewidth=1.5,
            )
            self._flow_lines[key] = line
        self.ax_flow.legend(loc="upper left", fontsize=7, facecolor="#2a2a3d",
                            edgecolor="#555555", labelcolor="#cccccc")

        # Pressure subplot (all red shades)
        self.ax_pressure.set_ylabel("Pressure (mmHg)", color="#cccccc", fontsize=9)
        self.ax_pressure.set_xlabel("Time (s)", color="#cccccc", fontsize=9)
        self._pressure_lines = {}
        for key in PRESSURE_KEYS:
            label = f"{key.upper()} [{PIN_LABELS[key]}]"
            (line,) = self.ax_pressure.plot(
                [], [], color=SENSOR_COLORS[key], label=label, linewidth=1.5,
            )
            self._pressure_lines[key] = line
        self.ax_pressure.legend(loc="upper left", fontsize=7, facecolor="#2a2a3d",
                                edgecolor="#555555", labelcolor="#cccccc")

        self._canvas = FigureCanvasTkAgg(self.fig, master=self)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_data(self, data: dict, elapsed_seconds: float):
        self._timestamps.append(elapsed_seconds)
        for key in self._data:
            self._data[key].append(data.get(key, 0.0))

        if len(self._timestamps) > MAX_GRAPH_POINTS:
            excess = len(self._timestamps) - MAX_GRAPH_POINTS
            self._timestamps = self._timestamps[excess:]
            for key in self._data:
                self._data[key] = self._data[key][excess:]

        t = self._timestamps
        for key, line in self._flow_lines.items():
            line.set_data(t, self._data[key])
        for key, line in self._pressure_lines.items():
            line.set_data(t, self._data[key])

        for ax in (self.ax_flow, self.ax_pressure):
            ax.relim()
            ax.autoscale_view()

        self._canvas.draw_idle()

    def clear(self):
        self._timestamps.clear()
        for key in self._data:
            self._data[key].clear()
        for line in self._flow_lines.values():
            line.set_data([], [])
        for line in self._pressure_lines.values():
            line.set_data([], [])
        self._canvas.draw_idle()
