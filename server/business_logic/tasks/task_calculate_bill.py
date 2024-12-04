from models.meter_reading import MeterReading
from models.task import Task
from server.business_logic.bill_calculation.bill_calculator import BillCalculator
from server.config import Config
from server.mock_memory.mock_readings_memory import MockReadingsMemory
from server.api.tasks.serialization.task_serialize_bill import TaskSerializeBill
from server.task_pipeline.task_manager import TaskManager
import logging


class TaskCalculateBill(Task):
    def __init__(self, reading: MeterReading, communication_data):
        print("\n=== TaskCalculateBill Initialization ===")
        print(f"Received reading for meter: {reading.meter_id}")
        print(f"Reading value: {reading.reading_value} {reading.reading_unit}")

        self.reading = reading
        self.calculator = BillCalculator(
            price_per_unit=Config.get_price_per_unit(),
            standing_charge=Config.get_standing_charge()
        )
        self.communication_data = communication_data

    def execute(self) -> None:
        print("\n=== Starting Bill Calculation ===")

        try:
            # Get and store readings
            print("Retrieving previous reading...")
            previous_reading = MockReadingsMemory.get_latest_reading(self.reading.meter_id)
            if previous_reading:
                print(f"Found previous reading: {previous_reading.reading_value} {previous_reading.reading_unit}")
            else:
                print("No previous reading found - this is an initial reading")

            print("Saving current reading to memory...")
            MockReadingsMemory.save_new_reading(self.reading)
            print("Reading saved successfully")

            # Calculate bill
            print("Calculating bill...")
            bill_data = self.calculator.calculate_bill(
                self.reading,
                previous_reading
            )
            print(f"Bill calculated - Total amount: £{bill_data.total_bill:.2f}")

            # Enqueue serialization task
            print("Enqueueing bill serialization task...")
            TaskManager.enqueue(
                TaskSerializeBill(
                    bill_data=bill_data,
                    communication_data=self.communication_data
                )
            )
            print("Bill serialization task enqueued successfully")

        except Exception as e:
            print(f"\n!!! Error in TaskCalculateBill !!!")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            raise

        print("\n=== Bill Calculation Completed Successfully ===")