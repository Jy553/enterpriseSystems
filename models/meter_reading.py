import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class MeterReading:
    meter_id: str
    reading_value: float
    reading_unit: str
    timestamp: datetime.datetime
    previous_reading: Optional[float] = None
    sequence_number: Optional[int] = None
    message_id: Optional[str] = None

    def __post_init__(self):
        if self.reading_value < 0:
            raise ValueError("Reading value cannot be negative")

        if self.previous_reading is not None and self.reading_value < self.previous_reading:
            raise ValueError("Current reading cannot be less than previous reading")