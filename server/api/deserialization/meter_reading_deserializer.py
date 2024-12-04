import json
from datetime import datetime
from models.meter_reading import MeterReading


class MeterReadingDeserializer:
    @classmethod
    def convert_reading_json_to_reading_object(cls, json_str: str) -> MeterReading:
        """Convert a JSON string to a MeterReading object."""
        print("\n=== Starting Deserialization ===")
        print(f"Raw JSON string received: {json_str}")

        try:
            data = json.loads(json_str)
            print(f"Parsed JSON data: {json.dumps(data, indent=2)}")
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse JSON: {str(e)}")
            raise

        print(f"\nChecking message type...")
        if "messageType" not in data:
            print("ERROR: No messageType field found in JSON")
            raise ValueError("Missing messageType field")

        print(f"Message type found: {data['messageType']}")
        if data["messageType"] != "READING":
            print(f"ERROR: Invalid message type: {data['messageType']}")
            raise ValueError(f"Invalid message type: {data['messageType']}")

        print("\nExtracting reading data...")
        try:
            reading_data = data["data"]
            print(f"Reading data extracted: {json.dumps(reading_data, indent=2)}")
        except KeyError:
            print("ERROR: No 'data' field found in JSON")
            raise ValueError("Missing data field")

        print("\nProcessing timestamp...")
        print(f"Raw timestamp value: {data.get('timestamp', 'NO TIMESTAMP FOUND')}")
        try:
            print("Attempting ISO format parsing...")
            timestamp = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
            print(f"Successfully parsed timestamp: {timestamp}")
        except ValueError as e:
            print(f"ISO parsing failed: {str(e)}")
            print("Attempting strptime parsing...")
            try:
                timestamp = datetime.strptime(data["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
                print(f"Successfully parsed timestamp with strptime: {timestamp}")
            except ValueError as e:
                print(f"ERROR: All timestamp parsing attempts failed: {str(e)}")
                raise

        print("\nCreating MeterReading object...")
        try:
            reading = MeterReading(
                meter_id=reading_data["meter_id"],
                reading_value=reading_data["reading_value"],
                reading_unit=reading_data["reading_unit"],
                timestamp=timestamp,
                previous_reading=reading_data.get("previous_reading"),
                sequence_number=reading_data.get("sequence_number"),
            )
            print("Successfully created MeterReading object:")
            print(f"  Meter ID: {reading.meter_id}")
            print(f"  Reading Value: {reading.reading_value}")
            print(f"  Reading Unit: {reading.reading_unit}")
            print(f"  Timestamp: {reading.timestamp}")
            print(f"  Previous Reading: {reading.previous_reading}")
            print(f"  Sequence Number: {reading.sequence_number}")
            return reading
        except KeyError as e:
            print(f"ERROR: Missing required field: {str(e)}")
            raise ValueError(f"Missing required field: {str(e)}")
        except Exception as e:
            print(f"ERROR: Failed to create MeterReading object: {str(e)}")
            raise
