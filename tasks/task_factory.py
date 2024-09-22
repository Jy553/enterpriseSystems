from tasks.concrete_tasks.alert_task import AlertTask
from tasks.concrete_tasks.billing_task import BillingTask
from tasks.concrete_tasks.meter_reading_task import MeterReadingTask


class TaskFactory:
    @staticmethod
    def create_task(task_type, task_info, is_priority=False):
        if task_type == "meter_reading":
            return MeterReadingTask(task_info, is_priority)
        elif task_type == "billing":
            return BillingTask(task_info, is_priority)
        elif task_type == "alert":
            return AlertTask(task_info)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
