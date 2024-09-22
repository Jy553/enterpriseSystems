import unittest
from queue import Full, Empty

from tasks.concrete_tasks.alert_task import AlertTask
from tasks.concrete_tasks.billing_task import BillingTask
from tasks.concrete_tasks.meter_reading_task import MeterReadingTask
from tasks.queues.normal_queue import NormalQueue


class TestNormalQueue(unittest.TestCase):
    def setUp(self):
        self.queue = NormalQueue(maxsize=2)

    def test_put_and_get(self):
        task = MeterReadingTask({"meter_id": "123", "reading": 100})
        self.queue.put(task)
        retrieved_task = self.queue.get()
        self.assertEqual(task, retrieved_task)

    def test_queue_size(self):
        task1 = MeterReadingTask({"meter_id": "123", "reading": 100})
        task2 = BillingTask({"client_id": "456", "amount": 50.0})
        self.queue.put(task1)
        self.queue.put(task2)
        self.assertEqual(self.queue.qsize(), 2)

    def test_queue_full(self):
        task1 = MeterReadingTask({"meter_id": "123", "reading": 100})
        task2 = BillingTask({"client_id": "456", "amount": 50.0})
        self.queue.put(task1, block=False)
        self.queue.put(task2, block=False)
        with self.assertRaises(Full):
            self.queue.put(AlertTask({"alert_type": "high_usage", "client_id": "789"}), block=False)

    def test_queue_empty(self):
        with self.assertRaises(Empty):
            self.queue.get(block=False)


if __name__ == '__main__':
    unittest.main()
