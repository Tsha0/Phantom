import tkinter as tk
from PIL import Image, ImageTk
from .constants import (
    CIRCUIT_IMAGE, SENSOR_POSITIONS, SENSOR_UNITS,
    OVERLAY_FLOW_COLOR, OVERLAY_PRESSURE_COLOR,
    DEFAULT_FLOW_PINS, DEFAULT_PRESSURE_PINS, BG_DARK,
)


class CircuitPanel(tk.Frame):
    """Displays the circuit diagram scaled to fill available space, with live sensor overlays.

    No scrollbars — the image scales to fit the canvas.
    Clicking a sensor overlay triggers the on_sensor_click callback.
    """

    def __init__(self, parent, on_sensor_click=None):
        super().__init__(parent, bg=BG_DARK)
        self._on_sensor_click = on_sensor_click
        self._text_ids = {}
        self._bg_ids = {}
        self._hit_areas = {}
        self._photo = None
        self._raw_image = None
        self._last_size = (0, 0)
        # Current pin assignments (mutable — updated from pin config UI)
        self._pin_labels = {}
        self._pin_labels.update(DEFAULT_FLOW_PINS)
        self._pin_labels.update(DEFAULT_PRESSURE_PINS)
        self._build()

    def _build(self):
        self.canvas = tk.Canvas(self, bg="#c8c8c8", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        try:
            self._raw_image = Image.open(CIRCUIT_IMAGE)
        except Exception:
            self._raw_image = None

        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_click)

    def _on_resize(self, event):
        w, h = event.width, event.height
        if abs(w - self._last_size[0]) < 5 and abs(h - self._last_size[1]) < 5:
            return
        self._last_size = (w, h)
        self._redraw(w, h)

    def _redraw(self, canvas_w, canvas_h):
        self.canvas.delete("all")
        self._text_ids.clear()
        self._bg_ids.clear()
        self._hit_areas.clear()

        if self._raw_image is None:
            return

        src_w, src_h = self._raw_image.size
        scale = min(canvas_w / src_w, canvas_h / src_h)
        new_w = max(int(src_w * scale), 1)
        new_h = max(int(src_h * scale), 1)

        resized = self._raw_image.resize((new_w, new_h), Image.LANCZOS)
        self._photo = ImageTk.PhotoImage(resized)

        x_off = (canvas_w - new_w) // 2
        y_off = (canvas_h - new_h) // 2
        self.canvas.create_image(x_off, y_off, anchor=tk.NW, image=self._photo)

        for key, (xf, yf) in SENSOR_POSITIONS.items():
            x = x_off + int(xf * new_w)
            y = y_off + int(yf * new_h)
            pin = self._pin_labels.get(key, "?")
            unit = SENSOR_UNITS.get(key, "")
            label = f"{key.upper()} [{pin}]"
            text = f"{label}: --  {unit}"

            color = OVERLAY_FLOW_COLOR if key.startswith("fl") else OVERLAY_PRESSURE_COLOR
            pad_x, pad_y = 65, 12

            bg_id = self.canvas.create_rectangle(
                x - pad_x, y - pad_y, x + pad_x, y + pad_y,
                fill="#1a1a2e", outline=color, width=1,
            )
            text_id = self.canvas.create_text(
                x, y, text=text, fill=color,
                font=("Consolas", 9, "bold"), anchor=tk.CENTER,
            )
            self._bg_ids[key] = bg_id
            self._text_ids[key] = text_id
            self._hit_areas[key] = (x - pad_x, y - pad_y, x + pad_x, y + pad_y)

    def _on_click(self, event):
        if not self._on_sensor_click:
            return
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        for key, (x1, y1, x2, y2) in self._hit_areas.items():
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                self._on_sensor_click(key)
                return

    def set_pin_labels(self, pin_map: dict):
        """Update pin labels and redraw overlays."""
        self._pin_labels.update(pin_map)
        w, h = self._last_size
        if w > 0 and h > 0:
            self._redraw(w, h)

    def update_readings(self, data: dict):
        for key, (xf, yf) in SENSOR_POSITIONS.items():
            if key in data and key in self._text_ids:
                pin = self._pin_labels.get(key, "?")
                unit = SENSOR_UNITS.get(key, "")
                label = f"{key.upper()} [{pin}]"
                text = f"{label}: {data[key]:.1f} {unit}"
                self.canvas.itemconfig(self._text_ids[key], text=text)
