from datetime import datetime

from client.models.bill import Bill
from client.models.message import Message
from models.bill_data import BillData
from models.task import Task
from server.api.tasks.task_send_bill import TaskSendBill
from server.task_pipeline.task_manager import TaskManager


class TaskSerializeBill(Task):
    def __init__(self, bill_data: BillData, communication_data):
        print("\n=== TaskSerializeBill Initialization ===")
        print(f"Received bill data for meter: {bill_data.meter_id}")
        print(f"Total bill amount: £{bill_data.total_bill:.2f}")

        self.bill_data = bill_data
        self.communication_data = communication_data

    def execute(self):
        """Create and send a properly formatted bill message."""
        print("\n=== Starting Bill Serialization ===")
        try:
            # First convert the bill data into the proper Bill model
            bill = Bill(
                meter_id=self.bill_data.meter_id,
                consumption=self.bill_data.consumption,
                billing_period=self.bill_data.billing_period,
                billing_period_start=self.bill_data.billing_period_start,
                billing_period_end=self.bill_data.billing_period_end,
                consumption_cost=self.bill_data.consumption_cost,
                total_standing_charge=self.bill_data.total_standing_charge,
                total_bill=self.bill_data.total_bill,
                is_initial_reading=self.bill_data.is_initial_reading
            )

            # Create a Message wrapper with current timestamp
            message = Message[Bill](
                messageType="BILL",
                timestamp=datetime.now(),
                data=bill
            )

            # Serialize the entire message to JSON
            bill_json_str = message.model_dump_json()
            print(f"Serialized JSON: {bill_json_str}")

            # Log the bill details for debugging
            print(f"Bill details:")
            print(f"  Meter ID: {bill.meter_id}")
            print(f"  Consumption: {bill.consumption:.2f} kWh")
            print(f"  Total Bill: £{bill.total_bill:.2f}")
            print(f"  Is Initial: {bill.is_initial_reading}")

            # Enqueue the send task with the properly formatted message
            print("Enqueueing bill send task...")
            TaskManager.enqueue(
                TaskSendBill(
                    bill_json=bill_json_str,
                    communication_data=self.communication_data
                )
            )
            print("Bill send task enqueued successfully")

        except Exception as e:
            print("\n!!! Error in TaskSerializeBill !!!")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print("Debug information:")
            print(f"BillData: {self.bill_data}")
            raise

        print("\n=== Bill Serialization Completed Successfully ===")
