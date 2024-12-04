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
    def __init__(self, reading: MeterReading):
        self.reading = reading

    def execute(self) -> None:
        try:
            # Validate the reading value
            BillDataValidator.validate_reading(self.reading.reading_value)

            # Validate timestamp
            BillDataValidator.validate_timestamp(self.reading.timestamp)

            # Get previous reading for sequence validation
            previous_reading = MockReadingsMemory.get_latest_reading(self.reading.meter_id)

            # Validate reading sequence if there's a previous reading
            BillDataValidator.validate_readings_sequence(self.reading, previous_reading)

            # If all validations pass, enqueue the calculate bill task
            TaskManager.enqueue(TaskCalculateBill(reading=self.reading))

        except ValueError as e:
            # Create and enqueue an alert for the validation failure
            alert = Alert(
                meter_id=self.reading.meter_id,
                message=self._get_user_friendly_message(str(e)),
                timestamp=datetime.now(),
                alert_type="VALIDATION_ERROR",
                reading_id=self.reading.message_id,
                severity="HIGH"
            )

            TaskManager.enqueue(TaskSerializeAlert(alert))
            raise

    @staticmethod
    def _get_user_friendly_message(error_message: str) -> str:
        """Convert technical error messages into user-friendly notifications."""
        if "cannot be negative" in error_message:
            return (f"Your meter reading shows negative consumption."
                    f"Please have your meter inspected for potential malfunction.")
        elif "cannot be less than previous" in error_message:
            return (f"Your meter reading is lower than the previous reading."
                    f"Please check your meter for proper operation.")
        elif "cannot be in the future" in error_message:
            return (f"Your meter reading shows a future timestamp."
                    f"Please verify your meter's date and time settings.")
        elif "billing period" in error_message:
            return (f"The time between meter readings is unusually long."
                    f"Please ensure regular meter readings are being submitted.")
        else:
            return (f"An issue was detected with your meter reading."
                    f"Please contact support for assistance.")
