import tkinter as tk
from tkinter import ttk
from .constants import (
    SERVO_TICK_MIN, SERVO_TICK_MAX, SERVO_TICK_DEFAULT, SERVO_PORTS,
    BG_PANEL, BG_CARD, FG_TEXT, FG_DIM, ACCENT_BLUE,
    DEFAULT_FLOW_PINS, DEFAULT_PRESSURE_PINS, DIGITAL_PINS, ANALOG_PINS,
    OVERLAY_FLOW_COLOR, OVERLAY_PRESSURE_COLOR,
)


class ControlPanel(tk.Frame):
    """Single-servo control with port selector, position slider, and submit button.
    Plus sensor pin configuration.
    """

    def __init__(self, parent, on_servo_command, on_pins_changed=None):
        super().__init__(parent, bg=BG_PANEL)
        self._on_servo_command = on_servo_command
        self._on_pins_changed = on_pins_changed
        self._pin_vars = {}
        self._build()

    def _build(self):
        # --- Servo Control ---
        tk.Label(
            self, text="Servo Control", font=("Segoe UI", 13, "bold"),
            bg=BG_PANEL, fg=FG_TEXT,
        ).pack(fill=tk.X, padx=8, pady=(10, 4))

        self._build_servo_card()

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

    def _build_servo_card(self):
        card = tk.Frame(self, bg=BG_CARD, padx=10, pady=8)
        card.pack(fill=tk.X, padx=6, pady=3)

        # Row 1: Port selector
        port_row = tk.Frame(card, bg=BG_CARD)
        port_row.pack(fill=tk.X, pady=(0, 6))

        tk.Label(
            port_row, text="Port:", font=("Segoe UI", 10, "bold"),
            bg=BG_CARD, fg=FG_TEXT,
        ).pack(side=tk.LEFT)

        self._port_var = tk.IntVar(value=0)
        port_combo = ttk.Combobox(
            port_row, textvariable=self._port_var,
            values=SERVO_PORTS, width=4, state="readonly",
        )
        port_combo.pack(side=tk.LEFT, padx=(6, 0), fill=tk.X, expand=True)

        # Row 2: Position label + entry
        pos_row = tk.Frame(card, bg=BG_CARD)
        pos_row.pack(fill=tk.X)
        pos_row.columnconfigure(0, weight=1)

        tk.Label(
            pos_row, text="Position:", font=("Segoe UI", 10, "bold"),
            bg=BG_CARD, fg=FG_TEXT,
        ).grid(row=0, column=0, sticky=tk.W)

        self._entry_var = tk.StringVar(value=str(SERVO_TICK_DEFAULT))
        entry = tk.Entry(
            pos_row, textvariable=self._entry_var, width=5,
            font=("Consolas", 10), bg="#2a2a40", fg=ACCENT_BLUE,
            insertbackground=ACCENT_BLUE, bd=1, relief=tk.FLAT,
            justify=tk.CENTER,
        )
        entry.grid(row=0, column=1, sticky=tk.E, padx=(4, 2))
        entry.bind("<Return>", lambda e: self._on_submit())

        tk.Label(
            pos_row, text="ticks", font=("Consolas", 10),
            bg=BG_CARD, fg=FG_DIM,
        ).grid(row=0, column=2, sticky=tk.E)

        # Row 3: Slider
        self._slider_var = tk.IntVar(value=SERVO_TICK_DEFAULT)
        slider = ttk.Scale(
            card,
            from_=SERVO_TICK_MIN,
            to=SERVO_TICK_MAX,
            orient=tk.HORIZONTAL,
            variable=self._slider_var,
            command=self._on_slider_move,
        )
        slider.pack(fill=tk.X, pady=(4, 2))

        # Info line
        tk.Label(
            card,
            text=f"Range {SERVO_TICK_MIN}-{SERVO_TICK_MAX} ticks  \u00b7  {SERVO_TICK_MIN}=closed  {SERVO_TICK_MAX}=open",
            font=("Consolas", 8), bg=BG_CARD, fg=FG_DIM,
        ).pack(fill=tk.X, anchor=tk.W)

        # Row 4: Submit button
        self._submit_btn = tk.Button(
            card, text="Send", font=("Segoe UI", 10, "bold"),
            bg=ACCENT_BLUE, fg="#000000", activebackground="#4a90d9",
            activeforeground="#000000",
            bd=0, padx=14, pady=6, cursor="hand2",
            command=self._on_submit,
        )
        self._submit_btn.pack(fill=tk.X, pady=(8, 0))

        # Set All buttons
        btn_row = tk.Frame(card, bg=BG_CARD)
        btn_row.pack(fill=tk.X, pady=(6, 0))
        btn_row.columnconfigure(0, weight=1)
        btn_row.columnconfigure(1, weight=1)

        tk.Button(
            btn_row, text="Set All Closed", font=("Segoe UI", 9, "bold"),
            bg="#555577", fg="#000000", activebackground="#666688",
            activeforeground="#000000",
            bd=0, padx=8, pady=4, cursor="hand2",
            command=self._set_all_closed,
        ).grid(row=0, column=0, sticky=tk.EW, padx=(0, 3))

        tk.Button(
            btn_row, text="Set All Open", font=("Segoe UI", 9, "bold"),
            bg="#555577", fg="#000000", activebackground="#666688",
            activeforeground="#000000",
            bd=0, padx=8, pady=4, cursor="hand2",
            command=self._set_all_open,
        ).grid(row=0, column=1, sticky=tk.EW, padx=(3, 0))

    def _on_slider_move(self, value):
        self._entry_var.set(str(self._slider_var.get()))

    def _on_submit(self):
        try:
            position = int(self._entry_var.get())
        except ValueError:
            position = self._slider_var.get()

        position = max(SERVO_TICK_MIN, min(SERVO_TICK_MAX, position))
        self._slider_var.set(position)
        self._entry_var.set(str(position))

        port = self._port_var.get()
        self._on_servo_command(port, position)

    def _set_all_closed(self):
        for port in SERVO_PORTS:
            self._on_servo_command(port, SERVO_TICK_MIN)
        self._port_var.set(0)
        self._slider_var.set(SERVO_TICK_MIN)
        self._entry_var.set(str(SERVO_TICK_MIN))

    def _set_all_open(self):
        for port in SERVO_PORTS:
            self._on_servo_command(port, SERVO_TICK_MAX)
        self._port_var.set(0)
        self._slider_var.set(SERVO_TICK_MAX)
        self._entry_var.set(str(SERVO_TICK_MAX))

    def _on_pin_change(self):
        if self._on_pins_changed:
            pin_map = {k: v.get() for k, v in self._pin_vars.items()}
            self._on_pins_changed(pin_map)

    def get_pin_assignments(self) -> dict:
        return {k: v.get() for k, v in self._pin_vars.items()}
