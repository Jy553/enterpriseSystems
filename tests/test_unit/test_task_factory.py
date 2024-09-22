import unittest

from tasks.concrete_tasks.alert_task import AlertTask
from tasks.concrete_tasks.billing_task import BillingTask
from tasks.concrete_tasks.meter_reading_task import MeterReadingTask
from tasks.task_factory import TaskFactory
from tasks.task import Task


class TestTaskFactory(unittest.TestCase):
    def setUp(self):
        self.factory = TaskFactory()

    def test_create_meter_reading_task(self):
        task = self.factory.create_task("meter_reading", {"meter_id": "123", "reading": 100})
        self.assertIsInstance(task, MeterReadingTask)

    def test_create_billing_task(self):
        task = self.factory.create_task("billing", {"client_id": "456", "amount": 50.0})
        self.assertIsInstance(task, BillingTask)

    def test_create_alert_task(self):
        task = self.factory.create_task("alert", {"alert_type": "high_usage", "client_id": "789"})
        self.assertIsInstance(task, AlertTask)

    def test_create_unknown_task_type(self):
        with self.assertRaises(ValueError):
            self.factory.create_task("unknown_task_type", {})

    def test_create_priority_task(self):
        task = self.factory.create_task("meter_reading", {"meter_id": "123", "reading": 100}, is_priority=True)
        self.assertIsInstance(task, MeterReadingTask)
        self.assertTrue(task.is_priority)

    def test_alert_task_always_priority(self):
        task = self.factory.create_task("alert", {"alert_type": "high_usage", "client_id": "789"})
        self.assertIsInstance(task, AlertTask)
        self.assertTrue(task.is_priority)

    if __name__ == '__main__':
        unittest.main()