from tasks.task import Task


# Used to execute the calculation of a bill
class BillingTask(Task):
    def __init__(self, task_info, is_priority=False):
        super().__init__(task_info, is_priority)

    def execute(self):
        print(f"Processing billing: {self.task_info}")
        # TODO: Complete billing execution
