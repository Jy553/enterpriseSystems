from datetime import datetime
from models.task import Task
from models.meter_reading import MeterReading
from models.alert import Alert
from server.mock_memory.mock_readings_memory import MockReadingsMemory
from server.business_logic.tasks.task_calculate_bill import TaskCalculateBill
from server.api.tasks.serialization.task_serialize_alert import TaskSerializeAlert
from server.business_logic.bill_calculation.bill_data_validator import BillDataValidator
from server.task_pipeline.task_manager import TaskManager


class TaskValidateReading(Task):
    def __init__(self, reading: MeterReading, communication_data):
        print("\n=== TaskValidateReading Initialization ===")
        print(f"Received reading object:")
        print(f"  Meter ID: {reading.meter_id}")
        print(f"  Reading Value: {reading.reading_value}")
        print(f"  Reading Unit: {reading.reading_unit}")
        print(f"  Timestamp: {reading.timestamp}")
        print(f"  Previous Reading: {reading.previous_reading}")
        print(f"  Sequence Number: {reading.sequence_number}")
        print(f"  Message ID: {reading.message_id}")
        print(f"Communication data: {communication_data}")
        self.reading = reading
        self.communication_data = communication_data

    def execute(self) -> None:
        print("\n=== Starting TaskValidateReading Execution ===")
        try:
            print("\n--- Starting Reading Value Validation ---")
            print(f"Current reading value: {self.reading.reading_value}")
            try:
                BillDataValidator.validate_reading(self.reading.reading_value)
                print("Reading value validation passed")
            except ValueError as e:
                print(f"Reading value validation failed: {str(e)}")
                raise

            print("\n--- Starting Timestamp Validation ---")
            print(f"Reading timestamp: {self.reading.timestamp}")
            print(f"Current time: {datetime.now()}")
            try:
                BillDataValidator.validate_timestamp(self.reading.timestamp)
                print("Timestamp validation passed")
            except ValueError as e:
                print(f"Timestamp validation failed: {str(e)}")
                raise

            print("\n--- Starting Previous Reading Retrieval ---")
            previous_reading = MockReadingsMemory.get_latest_reading(self.reading.meter_id)
            if previous_reading:
                print("Found previous reading:")
                print(f"  Previous Reading Value: {previous_reading.reading_value}")
                print(f"  Previous Reading Timestamp: {previous_reading.timestamp}")
            else:
                print("No previous reading found in storage")

            print("\n--- Starting Reading Sequence Validation ---")
            try:
                print(f"Validating sequence between:")
                print(f"  Current Reading: {self.reading.reading_value} at {self.reading.timestamp}")
                if previous_reading:
                    print(f"  Previous Reading: {previous_reading.reading_value} at {previous_reading.timestamp}")
                else:
                    print("  No previous reading to validate sequence against")

                BillDataValidator.validate_readings_sequence(self.reading, previous_reading)
                print("Reading sequence validation passed")
            except ValueError as e:
                print(f"Reading sequence validation failed: {str(e)}")
                raise

            print("\n--- All Validations Passed - Enqueueing Bill Calculation ---")
            print("Creating TaskCalculateBill...")
            try:
                bill_task = TaskCalculateBill(
                    reading=self.reading,
                    communication_data=self.communication_data)
                TaskManager.enqueue(bill_task)
                print("Successfully enqueued bill calculation task")
            except Exception as e:
                print(f"Failed to enqueue bill calculation task: {str(e)}")
                print(f"Error type: {type(e).__name__}")
                raise

        except ValueError as e:
            print("\n!!! Validation Failed - Creating Alert !!!")
            print(f"Original error: {str(e)}")

            print("\n--- Creating User-Friendly Alert Message ---")
            friendly_message = self._get_user_friendly_message(str(e))
            print(f"Converted to friendly message: {friendly_message}")

            print("\n--- Creating Alert Object ---")
            alert = Alert(
                meter_id=self.reading.meter_id,
                message=friendly_message,
                timestamp=datetime.now(),
                alert_type="VALIDATION_ERROR",
                reading_id=self.reading.message_id,
                severity="HIGH"
            )
            print("Alert object created successfully")

            print("\n--- Enqueueing Alert Serialization Task ---")
            try:
                TaskManager.enqueue(
                    TaskSerializeAlert(
                        alert=alert,
                        communication_data=self.communication_data))
                print("Successfully enqueued alert serialization task")
            except Exception as e:
                print(f"Failed to enqueue alert serialization task: {str(e)}")
                print(f"Error type: {type(e).__name__}")
                raise

            print("\n--- Re-raising Original Validation Error ---")
            raise

        print("\n=== TaskValidateReading Completed Successfully ===")
        print("=============================================")

    @staticmethod
    def _get_user_friendly_message(error_message: str) -> str:
        """Convert technical error messages into user-friendly notifications."""
        print("\n--- Converting Error to User-Friendly Message ---")
        print(f"Original error message: {error_message}")

        friendly_message = None
        if "cannot be negative" in error_message:
            friendly_message = ("Your meter reading shows negative consumption. "
                                "Please have your meter inspected for potential malfunction.")
        elif "cannot be less than previous" in error_message:
            friendly_message = ("Your meter reading is lower than the previous reading. "
                                "Please check your meter for proper operation.")
        elif "cannot be in the future" in error_message:
            friendly_message = ("Your meter reading shows a future timestamp. "
                                "Please verify your meter's date and time settings.")
        elif "billing period" in error_message:
            friendly_message = ("The time between meter readings is unusually long. "
                                "Please ensure regular meter readings are being submitted.")
        else:
            friendly_message = ("An issue was detected with your meter reading. "
                                "Please contact support for assistance.")

        print(f"Converted to friendly message: {friendly_message}")
        return friendly_message
