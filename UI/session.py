import csv
import os
from datetime import datetime
from .constants import DATA_DIR, SENSOR_KEYS


class SessionRecorder:
    """Records sensor readings during a session. Data is only exported when save() is called."""

    def __init__(self):
        self._recording = False
        self._data = []

    @property
    def is_recording(self):
        return self._recording

    def start(self):
        self._recording = True
        self._data.clear()

    def stop(self):
        """Stop recording. Data is kept in memory until save() or start() is called."""
        self._recording = False

    def record(self, data: dict):
        if not self._recording:
            return
        entry = {"timestamp": datetime.now().isoformat()}
        entry.update(data)
        self._data.append(entry)

    def save(self) -> str | None:
        """Write collected data to a timestamped CSV file. Returns path, or None if no data."""
        if not self._data:
            return None
        os.makedirs(DATA_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = os.path.join(DATA_DIR, f"Session_{timestamp}.csv")

        fieldnames = ["timestamp"] + SENSOR_KEYS
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in self._data:
                writer.writerow({k: row.get(k, "") for k in fieldnames})

        return filename

    @property
    def point_count(self):
        return len(self._data)

    @property
    def has_data(self):
        return len(self._data) > 0
