import unittest

from tasks.concrete_tasks.alert_task import AlertTask
from tasks.concrete_tasks.billing_task import BillingTask
from tasks.concrete_tasks.meter_reading_task import MeterReadingTask
from tasks.task import Task


class TestTask(unittest.TestCase):
    def test_task_creation(self):
        task = MeterReadingTask({"meter_id": "123", "reading": 100})
        self.assertIsInstance(task, Task)
        self.assertIsInstance(task, MeterReadingTask)
        self.assertEqual(task.task_info, {"meter_id": "123", "reading": 100})

    def test_task_unique_identifier(self):
        task1 = MeterReadingTask({})
        task2 = MeterReadingTask({})
        self.assertNotEqual(task1.task_id, task2.task_id)

    def test_task_info(self):
        info = {"client_id": "456", "amount": 50.0}
        task = BillingTask(info)
        self.assertEqual(task.task_info, info)

    def test_task_disposal(self):
        task = AlertTask({})
        self.assertFalse(task.is_disposed)
        task.dispose()
        self.assertTrue(task.is_disposed)

    def test_meter_reading_task_execute(self):
        task = MeterReadingTask({"meter_id": "123", "reading": 100})
        # Here we're testing that execute method doesn't raise an exception
        # In a real scenario, we'd mock any dependencies and check for expected side effects
        task.execute()

    def test_billing_task_execute(self):
        task = BillingTask({"client_id": "456", "amount": 50.0})
        task.execute()

    def test_alert_task_execute(self):
        task = AlertTask({"alert_type": "high_usage", "client_id": "789"})
        task.execute()

    def test_cannot_instantiate_abstract_task(self):
        with self.assertRaises(TypeError):
            Task({})

    def test_task_priority(self):
        normal_task = MeterReadingTask({"meter_id": "123", "reading": 100})
        self.assertFalse(normal_task.is_priority)

        priority_task = MeterReadingTask({"meter_id": "456", "reading": 200}, is_priority=True)
        self.assertTrue(priority_task.is_priority)

    def test_alert_task_default_priority(self):
        alert_task = AlertTask({"alert_type": "high_usage", "client_id": "789"})
        self.assertTrue(alert_task.is_priority)

    def test_alert_task_priority_override(self):
        non_priority_alert = AlertTask({"alert_type": "low_battery", "client_id": "101"}, is_priority=False)
        self.assertFalse(non_priority_alert.is_priority)

    if __name__ == '__main__':
        unittest.main()
