import time
import unittest

from tasks.concrete_tasks.alert_task import AlertTask
from tasks.concrete_tasks.meter_reading_task import MeterReadingTask
from tasks.queues.priority_queue import PriorityQueue


class TestPriorityQueue(unittest.TestCase):
    def setUp(self):
        self.queue = PriorityQueue(maxsize=3)

    def test_priority_order(self):
        low_priority = MeterReadingTask({"meter_id": "123", "reading": 100})
        high_priority = AlertTask({"alert_type": "high_usage", "client_id": "789"})

        self.queue.put(low_priority)
        self.queue.put(high_priority)

        self.assertEqual(self.queue.get(), high_priority)
        self.assertEqual(self.queue.get(), low_priority)

    def test_fifi_for_same_priority(self):
        task1 = AlertTask({"alert_type": "high_usage", "client_id": "789"})
        time.sleep(0.01)
        task2 = AlertTask({"alert_type": "very_high_usage", "client_id": "101"})

        self.queue.put(task1)
        self.queue.put(task2)

        self.assertEqual(self.queue.get(), task1)
        self.assertEqual(self.queue.get(), task2)