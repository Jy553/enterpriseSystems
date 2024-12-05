from models.task import Task
from models.alert import Alert
from server.api.serialization.alert_serializer import AlertSerializer
from server.api.tasks.task_send_alert import TaskSendAlert
from server.task_pipeline.task_manager import TaskManager


class TaskSerializeAlert(Task):
    def __init__(self, alert: Alert, communication_data):
        self.alert = alert
        self.communication_data = communication_data

    def execute(self) -> None:
        print(f"\nDEBUG - Serializing alert for meter {self.alert.meter_id}")

        # Serialize the alert
        alert_json = AlertSerializer.alert_to_json(self.alert)

        print(f"Serialized alert: {alert_json}")

        # Enqueue the send alert task
        TaskManager.enqueue(
            TaskSendAlert(
                meter_id=self.alert.meter_id,
                alert_message=self.alert.message,
                communication_data=self.communication_data
            ))
