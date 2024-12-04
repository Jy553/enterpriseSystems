from models.task import Task
from server.api.deserialization.meter_reading_deserializer import MeterReadingDeserializer
from server.business_logic.tasks.task_validate_reading import TaskValidateReading
from server.task_pipeline.task_manager import TaskManager


class TaskDeserializeReading(Task):
    def __init__(self, reading_json: str):
        self.reading_json = reading_json

    def execute(self) -> None:
        # Deserialize the reading
        reading = MeterReadingDeserializer.convert_reading_json_to_reading_object(self.reading_json)
        print(f"Successfully deserialized reading for meter {reading.meter_id}")
        # Enqueue the validation task
        TaskManager.enqueue(TaskValidateReading(reading=reading))
