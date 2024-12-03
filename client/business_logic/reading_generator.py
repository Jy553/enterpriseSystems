import random
import uuid
from datetime import datetime
from typing import Optional
from models.meter_reading import MeterReading


class ReadingGenerator:
    def __init__(self):
        self.previous_reading_value: Optional[float] = None
        self.sequence_number: Optional[int] = None

    def generate_reading(self, meter_id: str) -> MeterReading:
        reading_unit = "kWh"
        timestamp = datetime.now()
        message_id = str(uuid.uuid4())

        if self.previous_reading_value is None:
            reading_value = random.uniform(0, 100)
        else:
            reading_value = self.previous_reading_value + random.uniform(0, 10)

        if self.sequence_number is None:
            sequence_number = 1
        else:
            sequence_number = self.sequence_number + 1

        reading = MeterReading(
            meter_id=meter_id,
            reading_value=reading_value,
            reading_unit=reading_unit,
            timestamp=timestamp,
            previous_reading=self.previous_reading_value,
            sequence_number=sequence_number,
            message_id=message_id
        )

        # Update internal state with the new reading value
        self.previous_reading_value = reading_value
        self.sequence_number = sequence_number

        return reading
