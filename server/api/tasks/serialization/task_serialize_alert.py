from models.task import Task
from models.alert import Alert
from server.api.alert_serializer import AlertSerializer
from server.business_logic.tasks.task_send_alert import TaskSendAlert
from server.task_pipeline.task_manager import TaskManager


class TaskSerializeAlert(Task):
    def __init__(self, alert: Alert):
        self.alert = alert

    def execute(self) -> None:
        print(f"\nDEBUG - Serializing alert for meter {self.alert.meter_id}")

        # Serialize the alert
        alert_json = AlertSerializer.to_json(self.alert)

        print(f"Serialized alert: {alert_json}")

        # Enqueue the send alert task
        TaskManager.enqueue(TaskSendAlert(
            meter_id=self.alert.meter_id,
            alert_message=self.alert.message
        ))
