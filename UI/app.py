#!/usr/bin/env python3
"""
Phantom GUI — graphical interface for the Dynamic Ventricular Phantom.

Usage:
    python run_gui.py

Requirements:
    pip install pyserial matplotlib pillow
"""
import tkinter as tk
from tkinter import ttk, messagebox
import time

from .constants import (
    POLL_INTERVAL_MS, SENSOR_KEYS,
    BG_DARK, BG_PANEL, BG_CARD, FG_TEXT, FG_DIM,
    ACCENT_GREEN, ACCENT_RED, ACCENT_BLUE,
)
from .connection import connect_controller
from .circuit_panel import CircuitPanel
from .control_panel import ControlPanel
from .graph_panel import GraphPanel
from .session import SessionRecorder
from .sensor_graph import SensorGraphWindow


class PhantomGUI(tk.Tk):
    """Main application window with dark modern theme."""

    def __init__(self):
        super().__init__()
        self.title("Phantom \u2014 Dynamic Ventricular Phantom")
        self.geometry("1300x850")
        self.minsize(1000, 650)
        self.configure(bg=BG_DARK)

        self._apply_theme()

        self.controller = None
        self._poll_job = None
        self._start_time = time.time()
        self._session = SessionRecorder()
        self._latest_data = {}
        self._graph_visible = True

        # Connect to Arduino or demo mode
        self.withdraw()
        self.controller = connect_controller(self)
        if self.controller is None:
            self.destroy()
            return
        self.deiconify()

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Send default pin assignments to Arduino on startup
        if self.controller:
            pin_map = self.control_panel.get_pin_assignments()
            self.controller.send_pin_config(pin_map)

        self._poll_sensors()

    def _apply_theme(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(".", background=BG_PANEL, foreground=FG_TEXT, fieldbackground=BG_CARD)
        style.configure("TScale", background=BG_CARD, troughcolor="#3a3a55")
        style.configure("TButton", background=BG_CARD, foreground=FG_TEXT,
                         padding=(12, 6), font=("Segoe UI", 10))
        style.map("TButton",
                  background=[("active", "#454565"), ("pressed", "#505070")])
        style.configure("TSeparator", background="#444466")
        style.configure("TCombobox", fieldbackground=BG_CARD, foreground="#000000")
        style.map("TCombobox",
                  foreground=[("readonly", "#000000")],
                  selectforeground=[("readonly", "#000000")])
        # Style the dropdown listbox
        self.option_add("*TCombobox*Listbox.foreground", "#000000")
        self.option_add("*TCombobox*Listbox.background", "#ffffff")

    def _build_ui(self):
        self._build_menu()

        # Main horizontal split: circuit (80%) | sidebar (20%)
        self._main_frame = tk.Frame(self, bg=BG_DARK)
        self._main_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self._main_frame.columnconfigure(0, weight=4)
        self._main_frame.columnconfigure(1, weight=1)
        self._main_frame.rowconfigure(0, weight=1)

        # Left: circuit diagram
        self.circuit_panel = CircuitPanel(self._main_frame, on_sensor_click=self._on_sensor_click)
        self.circuit_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 4))

        # Right sidebar (scrollable)
        sidebar_outer = tk.Frame(self._main_frame, bg=BG_PANEL)
        sidebar_outer.grid(row=0, column=1, sticky="nsew")

        sidebar_canvas = tk.Canvas(sidebar_outer, bg=BG_PANEL, highlightthickness=0)
        sidebar_scroll = tk.Scrollbar(sidebar_outer, orient=tk.VERTICAL, command=sidebar_canvas.yview)
        sidebar_canvas.configure(yscrollcommand=sidebar_scroll.set)

        sidebar_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        sidebar_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._sidebar = tk.Frame(sidebar_canvas, bg=BG_PANEL)
        sidebar_canvas.create_window((0, 0), window=self._sidebar, anchor=tk.NW)
        self._sidebar.bind("<Configure>",
            lambda e: sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all")))
        # Enable mousewheel scrolling
        sidebar_canvas.bind_all("<MouseWheel>",
            lambda e: sidebar_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self._build_sidebar()

        # Bottom: live graph (retractable)
        self._graph_toggle_frame = tk.Frame(self, bg=BG_DARK)
        self._graph_toggle_frame.pack(fill=tk.X, padx=6)

        self._graph_toggle_btn = tk.Button(
            self._graph_toggle_frame,
            text="\u25bc  Live Sensor Data",
            font=("Segoe UI", 9, "bold"),
            bg=BG_CARD, fg=FG_TEXT, activebackground="#454565",
            bd=0, padx=10, pady=4, cursor="hand2",
            command=self._toggle_graph,
        )
        self._graph_toggle_btn.pack(fill=tk.X)

        self._graph_container = tk.Frame(self, bg=BG_DARK)
        self._graph_container.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

        self.graph_panel = GraphPanel(self._graph_container)
        self.graph_panel.pack(fill=tk.BOTH, expand=True)

    def _build_sidebar(self):
        sidebar = self._sidebar

        # Connection status bar
        mode = "Demo Mode" if self.controller.demo_mode else self.controller.port
        status_color = ACCENT_GREEN if not self.controller.demo_mode else "#facc15"
        status_frame = tk.Frame(sidebar, bg=BG_CARD, padx=10, pady=6)
        status_frame.pack(fill=tk.X, padx=8, pady=(8, 4))
        tk.Label(
            status_frame, text="\u25cf", font=("Arial", 10),
            bg=BG_CARD, fg=status_color,
        ).pack(side=tk.LEFT)
        tk.Label(
            status_frame, text=f"  {mode}", font=("Consolas", 9),
            bg=BG_CARD, fg=FG_TEXT,
        ).pack(side=tk.LEFT)

        # Servo control + pin config
        self.control_panel = ControlPanel(
            sidebar, self._on_servo_command,
            on_pins_changed=self._on_pins_changed,
        )
        self.control_panel.pack(fill=tk.X, padx=8, pady=4)

        # Session controls
        session_frame = tk.Frame(sidebar, bg=BG_CARD, padx=10, pady=8)
        session_frame.pack(fill=tk.X, padx=8, pady=4)

        tk.Label(
            session_frame, text="Session", font=("Segoe UI", 11, "bold"),
            bg=BG_CARD, fg=FG_TEXT,
        ).pack(anchor=tk.W, pady=(0, 6))

        btn_row = tk.Frame(session_frame, bg=BG_CARD)
        btn_row.pack(fill=tk.X)

        self._session_btn = tk.Button(
            btn_row, text="\u25b6  Start", font=("Segoe UI", 10, "bold"),
            bg=ACCENT_GREEN, fg="#1a1a2e", activebackground="#66d9a0",
            bd=0, padx=14, pady=6, cursor="hand2",
            command=self._toggle_session,
        )
        self._session_btn.pack(side=tk.LEFT, padx=(0, 6))

        self._save_btn = tk.Button(
            btn_row, text="\U0001f4be  Save", font=("Segoe UI", 10),
            bg=ACCENT_BLUE, fg="#ffffff", activebackground="#4a90d9",
            bd=0, padx=14, pady=6, cursor="hand2",
            state=tk.DISABLED, command=self._save_session,
        )
        self._save_btn.pack(side=tk.LEFT)

        self._session_status = tk.Label(
            session_frame, text="No active session", font=("Segoe UI", 9),
            bg=BG_CARD, fg=FG_DIM,
        )
        self._session_status.pack(anchor=tk.W, pady=(6, 0))

        # Sensor click hint
        hint_frame = tk.Frame(sidebar, bg=BG_PANEL)
        hint_frame.pack(fill=tk.X, padx=8, pady=(8, 4))
        tk.Label(
            hint_frame, text="Click a sensor on the circuit\nto open its live graph",
            font=("Segoe UI", 9), bg=BG_PANEL, fg=FG_DIM, justify=tk.CENTER,
        ).pack()

    def _build_menu(self):
        menubar = tk.Menu(self, bg=BG_PANEL, fg=FG_TEXT, activebackground=BG_CARD)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0, bg=BG_PANEL, fg=FG_TEXT)
        file_menu.add_command(label="Clear Graph", command=self._clear_graph)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_menu)

    # --- Graph toggle ---

    def _toggle_graph(self):
        if self._graph_visible:
            self._graph_container.pack_forget()
            self._graph_toggle_btn.config(text="\u25b6  Live Sensor Data")
            self._graph_visible = False
        else:
            self._graph_container.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))
            self._graph_toggle_btn.config(text="\u25bc  Live Sensor Data")
            self._graph_visible = True

    # --- Polling ---

    def _poll_sensors(self):
        raw = self.controller.request_sensor_data()
        data = self._parse_sensor_csv(raw)
        elapsed = time.time() - self._start_time
        self._latest_data = data

        self.circuit_panel.update_readings(data)
        if self._graph_visible:
            self.graph_panel.update_data(data, elapsed)

        # Update open sensor graph windows
        for key, val in data.items():
            if key in SensorGraphWindow._open_windows:
                try:
                    SensorGraphWindow._open_windows[key].update_data(val, elapsed)
                except tk.TclError:
                    pass

        if self._session.is_recording:
            self._session.record(data)
            self._session_status.config(
                text=f"Recording\u2026 ({self._session.point_count} points)"
            )

        self._poll_job = self.after(POLL_INTERVAL_MS, self._poll_sensors)

    @staticmethod
    def _parse_sensor_csv(raw: str) -> dict:
        parts = raw.split(",")
        data = {}
        for i, key in enumerate(SENSOR_KEYS):
            try:
                data[key] = float(parts[i]) if i < len(parts) else 0.0
            except ValueError:
                data[key] = 0.0
        return data

    # --- Callbacks ---

    def _on_servo_command(self, port, position):
        self.controller.send_servo_command(port, position)

    def _on_pins_changed(self, pin_map: dict):
        self.circuit_panel.set_pin_labels(pin_map)
        if self.controller:
            self.controller.send_pin_config(pin_map)

    def _on_sensor_click(self, sensor_key):
        SensorGraphWindow.open_for(self, sensor_key)

    def _toggle_session(self):
        if self._session.is_recording:
            self._session.stop()
            self._session_btn.config(text="\u25b6  Start", bg=ACCENT_GREEN, fg="#1a1a2e")
            self._session_status.config(
                text=f"Stopped ({self._session.point_count} points). Click Save to export."
            )
            if self._session.has_data:
                self._save_btn.config(state=tk.NORMAL)
        else:
            self._session.start()
            self._session_btn.config(text="\u25a0  Stop", bg=ACCENT_RED, fg="#ffffff")
            self._session_status.config(text="Recording\u2026 (0 points)")
            self._save_btn.config(state=tk.DISABLED)

    def _save_session(self):
        filepath = self._session.save()
        if filepath:
            self._session_status.config(text=f"Saved: {filepath}")
            self._save_btn.config(state=tk.DISABLED)
            messagebox.showinfo("Session Saved", f"Data exported to:\n{filepath}")
        else:
            self._session_status.config(text="No data to save")

    def _clear_graph(self):
        self.graph_panel.clear()
        self._start_time = time.time()

    def _on_close(self):
        if self._poll_job:
            self.after_cancel(self._poll_job)
        for win in list(SensorGraphWindow._open_windows.values()):
            try:
                win.destroy()
            except tk.TclError:
                pass
        SensorGraphWindow._open_windows.clear()
        if self.controller:
            self.controller.close()
        self.destroy()


def main():
    app = PhantomGUI()
    app.mainloop()


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    from UI.app import main as _main
    _main()
