from models.task import Task


class TaskSendBill(Task):
    def __init__(self, bill_json: str):
        self.bill_json = bill_json

    def execute(self):  # Must implement execute() as it's required by the Task base class
        # to be implemented
        pass