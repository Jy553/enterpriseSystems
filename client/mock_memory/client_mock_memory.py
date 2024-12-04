import threading
from typing import Optional, Dict, List, Tuple
from datetime import datetime
from models.bill_data import BillData
from models.meter_reading import MeterReading


class ClientMockMemory:
    def __init__(self):
        self._readings: Dict[str, List[Tuple[datetime, MeterReading]]] = {}
        self._bills: Dict[str, List[Tuple[datetime, BillData]]] = {}
        self._lock = threading.Lock()

    def get_latest_meter_reading(self, meter_id: str) -> Optional[MeterReading]:
        with self._lock:
            if meter_id not in self._readings or not self._readings[meter_id]:
                return None
            return self._readings[meter_id][-1][1]  # Return last element because list already sorted

    def save_new_meter_reading(self, reading: MeterReading):
        with self._lock:
            if reading.meter_id not in self._readings:
                self._readings[reading.meter_id] = []
            self._readings[reading.meter_id].append((reading.timestamp, reading))
            # Sort the list by timestamp after adding new reading
            self._readings[reading.meter_id].sort(key=lambda x: x[0])

    def get_latest_meter_bill(self, meter_id: str) -> Optional[BillData]:
        with self._lock:
            if meter_id not in self._bills or not self._bills[meter_id]:
                return None
            return self._bills[meter_id][-1][1]  # Return last element because list already sorted

    def save_new_bill(self, bill: BillData):
        with self._lock:
            if bill.meter_id not in self._bills:
                self._bills[bill.meter_id] = []
            self._bills[bill.meter_id].append((bill.timestamp, bill))
            # Sort the list by timestamp after adding new bill
            self._bills[bill.meter_id].sort(key=lambda x: x[0])
