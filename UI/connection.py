import sys
import os
import tkinter as tk
from tkinter import ttk

# Add project root to path so we can import from Phantom_UI.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from PhantomController import PhantomController, list_serial_ports


class PortSelectionDialog(tk.Toplevel):
    """Modal dialog for selecting a serial port or demo mode."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Phantom — Connect")
        self.resizable(False, False)
        self.grab_set()

        self.selected_port = None
        self.demo_mode = False

        # Center on screen
        self.geometry("400x350")
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 400) // 2
        y = (self.winfo_screenheight() - 350) // 2
        self.geometry(f"+{x}+{y}")

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _build_ui(self):
        tk.Label(self, text="Select Serial Port", font=("Arial", 14, "bold")).pack(
            pady=(15, 5)
        )

        # Port listbox
        frame = tk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.port_list = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Consolas", 10))
        self.port_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.port_list.yview)

        # Populate ports
        self.ports = list_serial_ports()
        if self.ports:
            for p in self.ports:
                marker = " << Arduino" if any(
                    s in p.device for s in ["usbmodem", "usbserial", "COM"]
                ) else ""
                self.port_list.insert(tk.END, f"{p.device}{marker}")
            self.port_list.selection_set(0)
        else:
            self.port_list.insert(tk.END, "(no ports detected)")

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Connect", command=self._on_connect).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Demo Mode", command=self._on_demo).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Cancel", command=self._on_cancel).pack(
            side=tk.LEFT, padx=5
        )

    def _on_connect(self):
        sel = self.port_list.curselection()
        if not sel or not self.ports:
            return
        self.selected_port = self.ports[sel[0]].device
        self.demo_mode = False
        self.destroy()

    def _on_demo(self):
        self.selected_port = None
        self.demo_mode = True
        self.destroy()

    def _on_cancel(self):
        self.selected_port = None
        self.demo_mode = False
        self.destroy()


def connect_controller(parent) -> PhantomController | None:
    """Show port selection dialog and return a connected PhantomController, or None if cancelled."""
    dialog = PortSelectionDialog(parent)
    parent.wait_window(dialog)

    if dialog.selected_port is None and not dialog.demo_mode:
        return None  # User cancelled

    return PhantomController(port=dialog.selected_port, demo_mode=dialog.demo_mode)
