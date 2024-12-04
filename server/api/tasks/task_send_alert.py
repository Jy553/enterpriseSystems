from models.task import Task


class TaskSendAlert(Task):
    def __init__(self, meter_id: str, alert_message: str):
        self.meter_id = meter_id
        self.alert_message = alert_message

    def execute(self) -> None:
        print(f"\nDEBUG - Sending alert for meter {self.meter_id}")
        print(f"Alert message: {self.alert_message}")
        # todo: implement
