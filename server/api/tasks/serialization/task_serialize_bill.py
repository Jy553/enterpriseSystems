from models.bill_data import BillData
from server.api.serialization.bill_serializer import BillSerializer
from models.task import Task
from server.api.tasks.task_send_bill import TaskSendBill
from server.task_pipeline.task_manager import TaskManager

class TaskSerializeBill(Task):
    def __init__(self,
                 bill_data: BillData):
        self.serializer = BillSerializer()
        self.bill_data = bill_data

    def execute(self):
        bill_json_str = self.serializer.bill_to_json(self.bill_data)
        TaskManager().enqueue(TaskSendBill(bill_json_str))
