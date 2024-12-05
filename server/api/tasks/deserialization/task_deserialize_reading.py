from models.task import Task
from server.api.deserialization.meter_reading_deserializer import MeterReadingDeserializer
from server.business_logic.tasks.task_validate_reading import TaskValidateReading
from server.task_pipeline.task_manager import TaskManager


class TaskDeserializeReading(Task):
    def __init__(self, reading_json: str, communication_data):
        print("\n=== TaskDeserializeReading Initialization ===")
        print(f"Received reading_json: {reading_json}")
        print(f"Received communication_data: {communication_data}")
        self.reading_json = reading_json
        self.communication_data = communication_data

    def execute(self) -> None:
        print("\n=== Starting TaskDeserializeReading Execution ===")
        print("Task details:")
        print(f"  Reading JSON length: {len(self.reading_json)} characters")
        print(f"  Communication data: {self.communication_data}")

        print("\n--- Starting Deserialization Process ---")
        try:
            print("Calling MeterReadingDeserializer.convert_reading_json_to_reading_object...")
            reading = MeterReadingDeserializer.convert_reading_json_to_reading_object(self.reading_json)
            print("\n--- Deserialization Successful ---")
            print("Reading object details:")
            print(f"  Meter ID: {reading.meter_id}")
            print(f"  Reading Value: {reading.reading_value}")
            print(f"  Reading Unit: {reading.reading_unit}")
            print(f"  Timestamp: {reading.timestamp}")
            print(f"  Previous Reading: {reading.previous_reading}")
            print(f"  Sequence Number: {reading.sequence_number}")
        except Exception as e:
            print("\n!!! DESERIALIZATION FAILED !!!")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print("Full error details:")
            import traceback
            print(traceback.format_exc())
            raise e

        print("\n--- Starting Validation Task Enqueue Process ---")
        try:
            print("Creating TaskValidateReading...")
            validation_task = TaskValidateReading(
                reading=reading,
                communication_data=self.communication_data
            )
            print("Successfully created validation task")

            print("Enqueueing validation task...")
            TaskManager.enqueue(validation_task)
            print("Successfully enqueued validation task")
        except Exception as e:
            print("\n!!! VALIDATION TASK ENQUEUE FAILED !!!")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            raise e

        print("\n=== TaskDeserializeReading Completed Successfully ===")
        print("Final reading object:")
        print(f"Reading Details:")
        print(f"  Meter ID: {reading.meter_id}")
        print(f"  Reading Value: {reading.reading_value}")
        print(f"  Reading Unit: {reading.reading_unit}")
        print(f"  Timestamp: {reading.timestamp}")
        print(f"  Previous Reading: {reading.previous_reading}")
        print(f"  Sequence Number: {reading.sequence_number}")
        print("=============================================")
