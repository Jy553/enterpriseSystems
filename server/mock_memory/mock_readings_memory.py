import threading
from typing import Optional, Dict, List, Tuple
from models.meter_reading import MeterReading
from datetime import datetime


class MockReadingsMemory:
    _instance = None
    _lock = threading.Lock()
    _readings: Dict[str, List[Tuple[datetime, MeterReading]]] = {}

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MockReadingsMemory, cls).__new__(cls)
                    if cls._readings is None:
                        cls._readings = {}
        return cls._instance

    @classmethod
    def get_latest_reading(cls, meter_id: str) -> Optional[MeterReading]:
        print("\n=== Getting Latest Reading ===")
        print(f"Attempting to get reading for meter: {meter_id}")

        try:
            with cls._lock:
                print("Lock acquired successfully")

                # Check if meter_id exists in readings
                if meter_id not in cls._readings:
                    print("No readings found for this meter ID")
                    return None

                # Get readings list for this meter
                meter_readings = cls._readings.get(meter_id, [])

                # Check if there are any readings
                if not meter_readings:
                    print("Reading list is empty for this meter ID")
                    return None

                # Get latest reading
                latest_reading = meter_readings[-1][1]
                print(f"Found reading: {latest_reading.reading_value} {latest_reading.reading_unit}")
                return latest_reading

        except Exception as e:
            print(f"Error retrieving reading: {str(e)}")
            raise e
        finally:
            print("Lock released")

    @classmethod
    def save_new_reading(cls, reading: MeterReading):
        """Save a new reading, preserving its timestamp."""
        print("\n=== Saving New Reading ===")
        print(f"Saving reading for meter: {reading.meter_id}")
        print(f"Reading value: {reading.reading_value} {reading.reading_unit}")
        print(f"Timestamp: {reading.timestamp}")

        try:
            with cls._lock:
                if reading.meter_id not in cls._readings:
                    cls._readings[reading.meter_id] = []

                # Store the reading with its timestamp
                cls._readings[reading.meter_id].append(
                    (reading.timestamp, reading)
                )

                # Sort readings by timestamp
                cls._readings[reading.meter_id].sort(key=lambda x: x[0])
                print(f"Reading saved successfully. Total readings for meter: {len(cls._readings[reading.meter_id])}")
                print(f"Current timestamp: {reading.timestamp}")

        except Exception as e:
            print(f"Error saving reading: {e}")
            raise
        finally:
            print("Save lock released")

    @classmethod
    def clear_readings(cls):
        """Clear all readings (useful for testing)"""
        with cls._lock:
            cls._readings.clear()
            print("All readings cleared")

    @classmethod
    def get_all_readings(cls, meter_id: str) -> List[MeterReading]:
        """Get all readings for a meter (useful for debugging)"""
        with cls._lock:
            if meter_id not in cls._readings:
                return []
            return [reading[1] for reading in cls._readings[meter_id]]
