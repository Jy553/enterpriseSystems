import json
from typing import Dict, Any

from models.meter_reading import MeterReading


class MeterReadingSerializer:
    MESSAGE_TYPE = "METER_READING"

    @classmethod
    def to_json(cls, reading: MeterReading) -> str:
        """Convert a MeterReading object to a JSON string."""
        return json.dumps(cls.to_dict(reading))

    @classmethod
    def to_dict(cls, reading: MeterReading) -> Dict[str, Any]:
        """Convert a MeterReading object to a dictionary matching the required format."""
        data = {
            "messageType": cls.MESSAGE_TYPE,
            "timestamp": reading.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "data": {
                "meterId": reading.meter_id,
                "readingValue": reading.reading_value,
                "readingUnit": reading.reading_unit,
                "sequenceNumber": reading.sequence_number
            },
            "messageId": reading.message_id
        }

        # Only include previousReading if it exists
        if reading.previous_reading is not None:
            data["data"]["previousReading"] = reading.previous_reading

        return data
