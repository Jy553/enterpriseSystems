import threading
from typing import Optional
from models.meter_reading import MeterReading


class MockReadingsMemory:
    def __init__(self):
        self._readings = []
        self._lock = threading.Lock()

    def get_reading(self, meter_id: str) -> Optional[MeterReading]:
        with self._lock:
            for _, reading in reversed(self._readings):
                if reading.meter_id == meter_id:
                    return reading
            return None

    def save_reading(self, reading_id: str, reading: MeterReading):
        with self._lock:
            self._readings.append((reading_id, reading))

    def get_latest_reading(self) -> Optional[MeterReading]:
        with self._lock:
            if self._readings:
                return self._readings[-1][1]
            else:
                return None
