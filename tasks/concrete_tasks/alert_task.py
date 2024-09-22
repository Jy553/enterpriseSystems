from tasks.task import Task


# Used to push alerts to the user. For example:
# > if there is a problem with the electricity grid
class AlertTask(Task):
    def __init__(self, task_info, is_priority=True):
        super().__init__(task_info, is_priority)

    def execute(self):
        print(f"Sending alert: {self.task_info}")
        # TODO: Complete send alert execution
