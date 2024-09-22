import time
import unittest
from queue import Empty
from unittest.mock import Mock, patch

from tasks.concrete_tasks.alert_task import AlertTask
from tasks.concrete_tasks.meter_reading_task import MeterReadingTask
from tasks.queues.normal_queue import NormalQueue
from tasks.queues.priority_queue import PriorityQueue
from tasks.task_executor import TaskExecutor


class TestTaskExecutor(unittest.TestCase):
    def setUp(self):
        self.normal_queue = Mock(spec=NormalQueue)
        self.priority_queue = Mock(spec=PriorityQueue)
        self.executor = TaskExecutor(self.normal_queue, self.priority_queue)

    def test_execute_priority_task(self):
        priority_task = AlertTask({"alert_type": "high_usage", "client_id": "789"})
        normal_task = MeterReadingTask({"meter_id": "123", "reading": 100})

        self.priority_queue.get.return_value = priority_task
        self.normal_queue.get.return_value = normal_task

        executed_task = self.executor.execute_next_task()

        self.assertEqual(executed_task, priority_task)
        self.priority_queue.get.assert_called_once()
        self.normal_queue.get.assert_not_called()

    def test_execute_normal_task_when_priority_empty(self):
        normal_task = MeterReadingTask({"meter_id": "123", "reading": 100})

        self.priority_queue.get.side_effect = Empty()
        self.normal_queue.get.return_value = normal_task

        executed_task = self.executor.execute_next_task()

        self.assertEqual(executed_task, normal_task)
        self.priority_queue.get.assert_called_once()
        self.normal_queue.get.assert_called_once()

    def test_no_tasks_available(self):
        self.priority_queue.get.side_effect = Empty()
        self.normal_queue.get.side_effect = Empty()

        with self.assertRaises(Exception):
            self.executor.execute_next_task()

    @patch('tasks.task_executor.time.sleep')
    def test_continuous_execution(self, mock_sleep):
        priority_task = AlertTask({"alert_type": "high_usage", "client_id": "789"})
        normal_task = MeterReadingTask({"meter_id": "123", "reading": 100})

        self.priority_queue.get.side_effect = [priority_task, normal_task, Empty()]
        self.normal_queue.get.side_effect = Empty()

        self.executor.run(max_tasks=2)

        self.assertEqual(self.priority_queue.get.call_count, 2)
        self.assertEqual(self.normal_queue.get.call_count, 0)
        mock_sleep.assert_not_called()

    @patch('tasks.task_executor.time.sleep')
    def test_execution_with_sleep(self, mock_sleep):
        priority_task = AlertTask({"alert_type": "high_usage", "client_id": "789"})

        self.priority_queue.get.side_effect = [priority_task, Empty(), Empty()]
        self.normal_queue.get.side_effect = Empty()

        self.executor.run(max_tasks=2)

        self.assertEqual(self.priority_queue.get.call_count, 2)
        self.assertEqual(self.normal_queue.get.call_count, 1)
        mock_sleep.assert_called_once()

    def test_task_execution_error_handling(self):
        mock_logger = Mock()
        executor = TaskExecutor(self.normal_queue, self.priority_queue, logger=mock_logger)

        error_task = Mock()
        error_task.execute.side_effect = Exception("Task execution failed")
        error_task.__str__ = lambda: "MockErrorTask"  # Remove 'self' from lambda

        self.priority_queue.get.return_value = error_task

        with self.assertRaises(Exception):
            executor.execute_next_task()

        mock_logger.error.assert_called_once_with("Error executing task: Task execution failed")

    def test_logging(self):
        mock_logger = Mock()
        executor = TaskExecutor(self.normal_queue, self.priority_queue, logger=mock_logger)

        task = MeterReadingTask({"meter_id": "123", "reading": 100})
        self.priority_queue.get.return_value = task

        executor.execute_next_task()

        mock_logger.info.assert_any_call(
            f"Executing task: {task.__class__.__name__}(task_id={task.task_id}, task_info={task.task_info})")
        mock_logger.info.assert_any_call(f"Task executed successfully: {task}")

    def test_priority_boost(self):
        normal_task = MeterReadingTask({"meter_id": "123", "reading": 100})
        normal_task.last_execution_attempt = time.time() - 100  # Task hasn't been executed for 100 seconds

        call_count = 0

        def side_effect_func(*_, **__):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Empty()
            else:
                return normal_task

        self.normal_queue.get.return_value = normal_task
        self.priority_queue.get.side_effect = side_effect_func

        executed_task = self.executor.execute_next_task()

        self.assertEqual(executed_task, normal_task)
        self.priority_queue.put.assert_called_once_with(normal_task)
        self.assertEqual(call_count, 2)  # Check the call count directly

    def test_run_in_thread(self):
        mock_logger = Mock()
        executor = TaskExecutor(self.normal_queue, self.priority_queue, logger=mock_logger)

        task1 = MeterReadingTask({"meter_id": "123", "reading": 100})
        task2 = AlertTask({"alert_type": "high_usage", "client_id": "789"})

        self.priority_queue.get.side_effect = [task1, task2, Empty(), Empty()]
        self.normal_queue.get.side_effect = Empty()

        thread = executor.run_in_thread()

        # Give some time for the thread to execute tasks
        time.sleep(0.1)

        executor.stop()
        thread.join()

        self.assertEqual(self.priority_queue.get.call_count, 3)
        self.assertEqual(self.normal_queue.get.call_count, 1)
        mock_logger.info.assert_any_call(
            f"Executing task: {task1.__class__.__name__}(task_id={task1.task_id}, task_info={task1.task_info})")
        mock_logger.info.assert_any_call(
            f"Executing task: {task2.__class__.__name__}(task_id={task2.task_id}, task_info={task2.task_info})")
        mock_logger.info.assert_any_call("No tasks available, sleeping...")

    def test_get_priority_task(self):
        mock_logger = Mock()
        executor = TaskExecutor(self.normal_queue, self.priority_queue, logger=mock_logger)

        priority_task = AlertTask({"alert_type": "high_usage", "client_id": "789"})
        self.priority_queue.get.return_value = priority_task

        task = executor.get_priority_task()

        self.assertEqual(task, priority_task)
        self.priority_queue.get.assert_called_once_with(block=False)

    def test_get_normal_task(self):
        mock_logger = Mock()
        executor = TaskExecutor(self.normal_queue, self.priority_queue, logger=mock_logger)

        normal_task = MeterReadingTask({"meter_id": "123", "reading": 100})
        self.normal_queue.get.return_value = normal_task

        task = executor.get_normal_task()

        self.assertEqual(task, normal_task)
        self.normal_queue.get.assert_called_once_with(block=False)

    def test_should_boost_priority(self):
        mock_logger = Mock()
        executor = TaskExecutor(self.normal_queue, self.priority_queue, logger=mock_logger, priority_boost_threshold=60)

        task = MeterReadingTask({"meter_id": "123", "reading": 100})
        task.last_execution_attempt = time.time() - 70  # 70 seconds ago

        self.assertTrue(executor.should_boost_priority(task))

        task.last_execution_attempt = time.time() - 50  # 50 seconds ago

        self.assertFalse(executor.should_boost_priority(task))

    def test_boost_task_priority(self):
        mock_logger = Mock()
        executor = TaskExecutor(self.normal_queue, self.priority_queue, logger=mock_logger)

        task = MeterReadingTask({"meter_id": "123", "reading": 100})

        executor.boost_task_priority(task)

        self.priority_queue.put.assert_called_once_with(task)
        mock_logger.info.assert_called_once_with(f"Boosting priority for task: {task}")

    def test_handle_task_error_with_retry(self):
        mock_logger = Mock()
        executor = TaskExecutor(self.normal_queue, self.priority_queue, logger=mock_logger, max_attempts=3)

        task = MeterReadingTask({"meter_id": "123", "reading": 100})
        exception = Exception("Test error")

        executor.handle_task_error(task, exception)

        self.assertEqual(task.attempts, 1)
        self.normal_queue.put.assert_called_once_with(task)
        mock_logger.error.assert_called_once_with("Error executing task: Test error")
        mock_logger.info.assert_called_once_with("Retrying task (attempt 1/3)")

    def test_handle_task_error_max_attempts_reached(self):
        mock_logger = Mock()
        executor = TaskExecutor(self.normal_queue, self.priority_queue, logger=mock_logger, max_attempts=3)

        task = MeterReadingTask({"meter_id": "123", "reading": 100})
        task.attempts = 2
        exception = Exception("Test error")

        executor.handle_task_error(task, exception)

        self.assertEqual(task.attempts, 3)
        self.normal_queue.put.assert_not_called()
        mock_logger.error.assert_called_with(f"Task failed after 3 attempts: {task}")

    def test_task_retry_mechanism(self):
        mock_logger = Mock()
        executor = TaskExecutor(self.normal_queue, self.priority_queue, logger=mock_logger, max_attempts=3)

        error_task = Mock()
        error_task.execute.side_effect = Exception("Task execution failed")
        error_task.attempts = 0

        self.priority_queue.get.return_value = error_task
        self.normal_queue.put = Mock()

        executor.execute_next_task()

        self.assertEqual(error_task.attempts, 1)
        self.normal_queue.put.assert_called_once_with(error_task)
        mock_logger.error.assert_called_with("Error executing task: Task execution failed")
        mock_logger.info.assert_called_with("Retrying task (attempt 1/3)")

    if __name__ == '__main__':
        unittest.main()
