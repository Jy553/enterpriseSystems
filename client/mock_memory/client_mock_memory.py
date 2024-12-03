import threading
from typing import Optional
from models.bill_data import BillData
from models.meter_reading import MeterReading


class ClientMockMemory:
    def __init__(self):
        self._readings = []
        self.bills = []
        self._lock = threading.Lock()

    def get_reading(self, reading_id: str) -> Optional[MeterReading]:
        with self._lock:
            for rid, reading in self._readings:
                if rid == reading_id:
                    return reading
            return None

    def save_reading(self, reading_id: str, reading: MeterReading):
        with self._lock:
            self._readings.append((reading_id, reading))

    def get_latest_reading(self) -> Optional[MeterReading]:
        with self._lock:
            if self._readings:
                return self._readings[-1][1]
            return None

    def get_bill(self, bill_id: str) -> Optional[BillData]:
        with self._lock:
            for rid, bill in self.bills:
                if rid == bill_id:
                    return bill
            return None

    def save_bill(self, bill_id: str, bill: BillData):
        with self._lock:
            self.bills.append((bill_id, bill))

    def get_latest_bill(self) -> Optional[BillData]:
        with self._lock:
            if self.bills:
                return self.bills[-1][1]
            else:
                return None
