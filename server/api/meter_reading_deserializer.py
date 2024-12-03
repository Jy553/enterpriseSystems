import json
from datetime import datetime
from models.meter_reading import MeterReading


class MeterReadingDeserializer:
    @classmethod
    def from_json(cls, json_str: str) -> MeterReading:
        """Convert a JSON string to a MeterReading object."""
        data = json.loads(json_str)

        if data["messageType"] != "METER_READING":
            raise ValueError(f"Invalid message type: {data['messageType']}")

        reading_data = data["data"]

        return MeterReading(
            meter_id=reading_data["meterId"],
            reading_value=reading_data["readingValue"],
            reading_unit=reading_data["readingUnit"],
            timestamp=datetime.strptime(data["timestamp"], "%Y-%m-%dT%H:%M:%SZ"),
            previous_reading=reading_data.get("previousReading"),
            sequence_number=reading_data.get("sequenceNumber"),
            message_id=data["messageId"]
        )