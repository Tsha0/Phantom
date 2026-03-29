import tkinter as tk
from tkinter import ttk
from .constants import (
    VALVE_CONFIG, VALVE_NAMES, BG_PANEL, BG_CARD, FG_TEXT, FG_DIM, ACCENT_BLUE,
    DEFAULT_FLOW_PINS, DEFAULT_PRESSURE_PINS, DIGITAL_PINS, ANALOG_PINS,
    OVERLAY_FLOW_COLOR, OVERLAY_PRESSURE_COLOR,
)


class ControlPanel(tk.Frame):
    """Valve sliders with manual entry, and sensor pin configuration.
    Fills the full width of its parent container.
    """

    def __init__(self, parent, on_conditions_changed, on_pins_changed=None):
        super().__init__(parent, bg=BG_PANEL)
        self._on_conditions_changed = on_conditions_changed
        self._on_pins_changed = on_pins_changed
        self._slider_vars = {}
        self._entry_vars = {}
        self._pin_vars = {}
        self._build()

    def _build(self):
        # --- Valve Controls ---
        tk.Label(
            self, text="Valve Controls", font=("Segoe UI", 13, "bold"),
            bg=BG_PANEL, fg=FG_TEXT,
        ).pack(fill=tk.X, padx=8, pady=(10, 4))

        for name in VALVE_NAMES:
            cfg = VALVE_CONFIG[name]
            self._build_slider_card(name, cfg)

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=6, pady=8)

        # --- Sensor Pin Configuration ---
        tk.Label(
            self, text="Sensor Pin Config", font=("Segoe UI", 13, "bold"),
            bg=BG_PANEL, fg=FG_TEXT,
        ).pack(fill=tk.X, padx=8, pady=(2, 4))

        pin_card = tk.Frame(self, bg=BG_CARD, padx=8, pady=8)
        pin_card.pack(fill=tk.X, padx=6, pady=4)
        pin_card.columnconfigure(1, weight=1)
        pin_card.columnconfigure(3, weight=1)

        # Flow sensors (digital pins)
        tk.Label(
            pin_card, text="Flow Sensors", font=("Segoe UI", 9, "bold"),
            bg=BG_CARD, fg=OVERLAY_FLOW_COLOR,
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 2))

        for i, (key, default_pin) in enumerate(DEFAULT_FLOW_PINS.items()):
            row = i + 1
            tk.Label(
                pin_card, text=f"{key.upper()}:", font=("Consolas", 9),
                bg=BG_CARD, fg=FG_TEXT,
            ).grid(row=row, column=0, sticky=tk.W, padx=(0, 4), pady=1)

            var = tk.StringVar(value=default_pin)
            self._pin_vars[key] = var
            combo = ttk.Combobox(
                pin_card, textvariable=var, values=DIGITAL_PINS,
                width=5, state="readonly",
            )
            combo.grid(row=row, column=1, sticky=tk.EW, pady=1)
            combo.bind("<<ComboboxSelected>>", lambda e: self._on_pin_change())

        # Pressure sensors (analog pins)
        tk.Label(
            pin_card, text="Pressure Sensors", font=("Segoe UI", 9, "bold"),
            bg=BG_CARD, fg=OVERLAY_PRESSURE_COLOR,
        ).grid(row=0, column=2, columnspan=2, sticky=tk.W, padx=(10, 0), pady=(0, 2))

        for i, (key, default_pin) in enumerate(DEFAULT_PRESSURE_PINS.items()):
            row = i + 1
            tk.Label(
                pin_card, text=f"{key.upper()}:", font=("Consolas", 9),
                bg=BG_CARD, fg=FG_TEXT,
            ).grid(row=row, column=2, sticky=tk.W, padx=(10, 4), pady=1)

            var = tk.StringVar(value=default_pin)
            self._pin_vars[key] = var
            combo = ttk.Combobox(
                pin_card, textvariable=var, values=ANALOG_PINS,
                width=5, state="readonly",
            )
            combo.grid(row=row, column=3, sticky=tk.EW, pady=1)
            combo.bind("<<ComboboxSelected>>", lambda e: self._on_pin_change())

    def _build_slider_card(self, name, cfg):
        card = tk.Frame(self, bg=BG_CARD, padx=8, pady=6)
        card.pack(fill=tk.X, padx=6, pady=3)

        # Top row: label + entry + % sign
        top = tk.Frame(card, bg=BG_CARD)
        top.pack(fill=tk.X)
        top.columnconfigure(0, weight=1)

        tk.Label(
            top, text=cfg["label"], font=("Segoe UI", 10, "bold"),
            bg=BG_CARD, fg=FG_TEXT,
        ).grid(row=0, column=0, sticky=tk.W)

        entry_var = tk.StringVar(value=str(cfg["default"]))
        self._entry_vars[name] = entry_var

        pct_label = tk.Label(
            top, text="%", font=("Consolas", 10),
            bg=BG_CARD, fg=FG_DIM,
        )
        pct_label.grid(row=0, column=2, sticky=tk.E)

        entry = tk.Entry(
            top, textvariable=entry_var, width=4,
            font=("Consolas", 10), bg="#2a2a40", fg=ACCENT_BLUE,
            insertbackground=ACCENT_BLUE, bd=1, relief=tk.FLAT,
            justify=tk.CENTER,
        )
        entry.grid(row=0, column=1, sticky=tk.E, padx=(4, 2))
        entry.bind("<Return>", lambda e, n=name: self._on_entry_submit(n))
        entry.bind("<FocusOut>", lambda e, n=name: self._on_entry_submit(n))

        # Slider — fills full width
        var = tk.IntVar(value=cfg["default"])
        self._slider_vars[name] = var

        slider = ttk.Scale(
            card,
            from_=cfg["pct_min"],
            to=cfg["pct_max"],
            orient=tk.HORIZONTAL,
            variable=var,
            command=lambda v, n=name: self._on_slider_move(n),
        )
        slider.pack(fill=tk.X, pady=(4, 2))
        slider.bind("<ButtonRelease-1>", lambda e: self._send_conditions())

        # Info line
        pmin, pmax = cfg["pulse_range"]
        tk.Label(
            card,
            text=f"Pulse {pmin}-{pmax}  \u00b7  Range {cfg['pct_min']}-{cfg['pct_max']}%",
            font=("Consolas", 8), bg=BG_CARD, fg=FG_DIM,
        ).pack(fill=tk.X, anchor=tk.W)

    def _on_slider_move(self, name):
        val = self._slider_vars[name].get()
        self._entry_vars[name].set(str(val))

    def _on_entry_submit(self, name):
        try:
            val = int(self._entry_vars[name].get())
            cfg = VALVE_CONFIG[name]
            val = max(cfg["pct_min"], min(cfg["pct_max"], val))
            self._slider_vars[name].set(val)
            self._entry_vars[name].set(str(val))
            self._send_conditions()
        except ValueError:
            self._entry_vars[name].set(str(self._slider_vars[name].get()))

    def _send_conditions(self):
        try:
            values = [self._slider_vars[n].get() for n in VALVE_NAMES]
        except tk.TclError:
            return
        self._on_conditions_changed(*values, 0, 0)

    def _on_pin_change(self):
        if self._on_pins_changed:
            pin_map = {k: v.get() for k, v in self._pin_vars.items()}
            self._on_pins_changed(pin_map)

    def get_pin_assignments(self) -> dict:
        return {k: v.get() for k, v in self._pin_vars.items()}

    def get_conditions(self):
        try:
            return tuple(self._slider_vars[n].get() for n in VALVE_NAMES) + (0, 0)
        except tk.TclError:
            return (50, 50, 50, 50, 0, 0)
