from tasks.task import Task


class AlertTask(Task):
    def __init__(self, task_info, is_priority=True):
        super().__init__(task_info, is_priority)

    def execute(self):
        print(f"Sending alert: {self.task_info}")
        # TODO: Complete send alert execution
