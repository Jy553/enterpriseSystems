import json
from models.meter_reading import MeterReading
from models.task import Task
from server.api.bill_serializer import BillSerializer
from server.business_logic.tasks.calculate_bill.bill_calculator import BillCalculator
from server.mock_memory.mock_readings_memory import MockReadingsMemory


class TaskCalculateBill(Task):
    def __init__(self,
                 reading: MeterReading,
                 storage: MockReadingsMemory,
                 price_per_unit: float,
                 standing_charge: float):
        self.reading = reading
        self.storage = storage
        self.calculator = BillCalculator(price_per_unit, standing_charge)
        self.serializer = BillSerializer()

    def execute(self) -> json:
        print("\nDEBUG - TaskCalculateBill executing:")
        print(f"Current Reading ID: {self.reading.message_id}")
        print(f"Looking for previous reading for meter: {self.reading.meter_id}")

        # Get previous reading if it exists
        previous_reading = self.storage.get_reading(self.reading.meter_id)
        if previous_reading:
            print(f"Found previous reading: {previous_reading.message_id}")
        else:
            print("No previous reading found")

        # Save the current reading for future calculations
        print("Saving current reading to storage")
        self.storage.save_reading(self.reading.message_id, self.reading)

        # Calculate the bill
        bill_data = self.calculator.calculate_bill(
            self.reading,
            previous_reading
        )

        # Format and return the bill
        return self.serializer.bill_to_json(bill_data)