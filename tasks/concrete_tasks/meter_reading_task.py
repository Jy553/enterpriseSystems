from tasks.task import Task


# Used to read the meter (client)
class MeterReadingTask(Task):
    def __init__(self, task_info, is_priority=False):
        super().__init__(task_info, is_priority)

    def execute(self):
        print(f"Processing meter reading: {self.task_info}")
        # TODO: Complete meter reading execution
