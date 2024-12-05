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
        self.reading = reading
        self.communication_data = communication_data

    def execute(self) -> None:
        print("\n=== Starting TaskValidateReading Execution ===")

        try:
            # Validate current reading value
            print("\n--- Starting Reading Value Validation ---")
            print(f"Current reading value: {self.reading.reading_value}")
            BillDataValidator.validate_reading(self.reading.reading_value)
            print("Reading value validation passed")

            # Validate timestamp
            print("\n--- Starting Timestamp Validation ---")
            print(f"Reading timestamp: {self.reading.timestamp}")
            print(f"Current time: {datetime.now()}")
            BillDataValidator.validate_timestamp(self.reading.timestamp)
            print("Timestamp validation passed")

            # Get previous reading
            print("\n--- Retrieving Previous Reading ---")
            try:
                previous_reading = MockReadingsMemory.get_latest_reading(self.reading.meter_id)
                if previous_reading:
                    print(f"Found previous reading: {previous_reading.reading_value} {previous_reading.reading_unit}")
                else:
                    print("No previous reading found - this is the first reading")
            except Exception as e:
                print(f"Error retrieving previous reading: {e}")
                previous_reading = None

            # Validate reading sequence if we have a previous reading
            if previous_reading:
                print("\n--- Validating Reading Sequence ---")
                try:
                    BillDataValidator.validate_readings_sequence(self.reading, previous_reading)
                    print("Reading sequence validation passed")
                except ValueError as e:
                    print(f"Reading sequence validation failed: {e}")
                    raise

            # Create and enqueue bill calculation task
            print("\n--- Creating Bill Calculation Task ---")
            try:
                bill_task = TaskCalculateBill(
                    reading=self.reading,
                    communication_data=self.communication_data
                )
                TaskManager.enqueue(bill_task)
                print("Successfully enqueued bill calculation task")
            except Exception as e:
                print(f"Failed to enqueue bill calculation task: {e}")
                raise

        except ValueError as e:
            print("\n!!! Validation Failed - Creating Alert !!!")
            print(f"Original error: {str(e)}")
            self._handle_validation_error(str(e))
            raise
        except Exception as e:
            print(f"\n!!! Unexpected Error: {str(e)} !!!")
            raise

        print("\n=== TaskValidateReading Completed Successfully ===")

    def _handle_validation_error(self, error_message: str):
        """Handle validation errors by creating and enqueueing an alert."""
        try:
            friendly_message = self._get_user_friendly_message(error_message)
            alert = Alert(
                meter_id=self.reading.meter_id,
                message=friendly_message,
                timestamp=datetime.now(),
                alert_type="VALIDATION_ERROR",
                reading_id=self.reading.message_id,
                severity="HIGH"
            )

            TaskManager.enqueue(
                TaskSerializeAlert(
                    alert=alert,
                    communication_data=self.communication_data
                )
            )
            print("Alert task enqueued successfully")
        except Exception as e:
            print(f"Failed to create/enqueue alert: {e}")
            raise

    @staticmethod
    def _get_user_friendly_message(error_message: str) -> str:
        """Convert technical error messages into user-friendly notifications."""
        if "cannot be negative" in error_message:
            return "Your meter reading shows negative consumption. Please have your meter inspected."
        elif "cannot be less than previous" in error_message:
            return "Your meter reading is lower than the previous reading. Please check your meter."
        elif "cannot be in the future" in error_message:
            return "Your meter reading shows a future timestamp. Please verify your meter's settings."
        elif "billing period" in error_message:
            return "The time between meter readings is unusually long. Please ensure regular readings."
        return "An issue was detected with your meter reading. Please contact support."
