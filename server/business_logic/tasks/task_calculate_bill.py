from models.meter_reading import MeterReading
from models.task import Task
from server.business_logic.bill_calculation.bill_calculator import BillCalculator
from server.config import Config
from server.mock_memory.mock_readings_memory import MockReadingsMemory
from server.api.tasks.serialization.task_serialize_bill import TaskSerializeBill
from server.task_pipeline.task_manager import TaskManager


class TaskCalculateBill(Task):
    def __init__(self, reading: MeterReading, communication_data):
        self.reading = reading
        self.calculator = BillCalculator(
            price_per_unit=Config.get_price_per_unit(),
            standing_charge=Config.get_standing_charge()
        )
        self.communication_data = communication_data

    def execute(self) -> None:
        previous_reading = MockReadingsMemory.get_latest_reading(self.reading.meter_id)
        MockReadingsMemory.save_new_reading(self.reading)

        bill_data = self.calculator.calculate_bill(
            self.reading,
            previous_reading
        )

        TaskManager.enqueue(
            TaskSerializeBill(
                bill_data=bill_data,
                communication_data=self.communication_data))
