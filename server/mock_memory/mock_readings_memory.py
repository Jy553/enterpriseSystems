import threading
from typing import Optional, Dict, List, Tuple
from models.meter_reading import MeterReading
from datetime import datetime


class MockReadingsMemory:
    _instance = None
    _lock = threading.Lock()
    _readings: Optional[Dict[str, List[Tuple[datetime, MeterReading]]]] = None

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MockReadingsMemory, cls).__new__(cls)
                cls._readings = {}
            return cls._instance

    @classmethod
    def get_latest_reading(cls, meter_id: str) -> Optional[MeterReading]:
        with cls._lock:
            if meter_id not in cls._readings or not cls._readings[meter_id]:
                return None
            return cls._readings[meter_id][-1][1]  # Return last element because list already sorted

    @classmethod
    def save_new_reading(cls, reading: MeterReading):
        with cls._lock:
            if reading.meter_id not in cls._readings:
                cls._readings[reading.meter_id] = []
            cls._readings[reading.meter_id].append((reading.timestamp, reading))
            # Sort the list by timestamp after adding new reading
            cls._readings[reading.meter_id].sort(key=lambda x: x[0])
