import unittest
from queue import Full
from unittest.mock import Mock
from tasks.concrete_tasks.alert_task import AlertTask
from tasks.concrete_tasks.billing_task import BillingTask
from tasks.concrete_tasks.meter_reading_task import MeterReadingTask
from tasks.task_scheduler import TaskScheduler, SchedulerError


class TestTaskScheduler(unittest.TestCase):
    def setUp(self):
        self.normal_queue = Mock()
        self.priority_queue = Mock()
        self.scheduler = TaskScheduler(self.normal_queue, self.priority_queue)

    def test_Schedule_meter_reading_task(self):
        task = MeterReadingTask({"meter_id": "123", "reading": 100})
        self.scheduler.schedule(task)
        self.normal_queue.put.assert_called_once_with(task, block=False)
        self.priority_queue.put.assert_not_called()

    def test_schedule_billing_task(self):
        task = BillingTask({"client_id": "456", "amount": 50.0})
        self.scheduler.schedule(task)
        self.normal_queue.put.assert_called_once_with(task, block=False)
        self.priority_queue.put.assert_not_called()

    def test_schedule_alert_task(self):
        task = AlertTask({"alert_type": "high_usage", "client_id": "789"})
        self.scheduler.schedule(task)
        self.priority_queue.put.assert_called_once_with(task, block=False)
        self.normal_queue.put.assert_not_called()

    def test_schedule_priority_task(self):
        task = MeterReadingTask({"meter_id": "123", "reading": 100}, is_priority=True)
        self.scheduler.schedule(task)
        self.priority_queue.put.assert_called_once_with(task, block=False)
        self.normal_queue.put.assert_not_called()

    def test_custom_priority_checker(self):
        def custom_checker(task):
            return task.task_info.get('reading', 0) > 1000

        scheduler = TaskScheduler(self.normal_queue, self.priority_queue, priority_checker=custom_checker)

        low_task = MeterReadingTask({"meter_id": "123", "reading": 100})
        scheduler.schedule(low_task)
        self.normal_queue.put.assert_called_once_with(low_task, block=False)

        high_task = MeterReadingTask({"meter_id": "456", "reading": 1500})
        scheduler.schedule(high_task)
        self.priority_queue.put.assert_called_once_with(high_task, block=False)

    def test_queue_full_error(self):
        self.normal_queue.put.side_effect = Full()
        self.priority_queue.put.side_effect = Full()
        task = MeterReadingTask({"meter_id": "123", "reading": 100})

        with self.assertRaises(SchedulerError):
            self.scheduler.schedule(task)

    def test_logging(self):
        mock_logger = Mock()
        scheduler = TaskScheduler(self.normal_queue, self.priority_queue, logger=mock_logger)

        task = MeterReadingTask({"meter_id": "123", "reading": 100})
        scheduler.schedule(task)

        mock_logger.info.assert_called_once_with(f"Scheduled task {task.task_id} to normal queue")

        priority_task = AlertTask({"alert_type": "high_usage", "client_id": "789"})
        scheduler.schedule(priority_task)

        mock_logger.info.assert_called_with(f"Scheduled priority task {priority_task.task_id} to priority queue")

    if __name__ == '__main__':
        unittest.main()
