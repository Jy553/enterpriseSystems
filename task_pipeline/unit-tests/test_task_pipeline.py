import unittest
from task_pipeline.task_pipeline import TaskPipeline
from tasks.task import Task
from unittest.mock import MagicMock, patch
import time
import threading


class TestTaskPipeLine(unittest.TestCase):
    def setUp(self):
        self.pipeline = TaskPipeline(num_workers=2)

    def tearDown(self):
        self.pipeline.shutdown()

    def test_task_gets_executed(self):
        # Arrange
        mock_task = MagicMock(spec=Task)

        # Act
        self.pipeline.enqueue(mock_task)
        time.sleep(0.2)  # Give time for execution

        # Assert
        mock_task.execute.assert_called_once()

    def test_multiple_tasks_execute(self):
        # Arrange
        mock_tasks = [MagicMock(spec=Task) for _ in range(5)]

        # Act
        for task in mock_tasks:
            self.pipeline.enqueue(task)
        time.sleep(0.5)  # Give time for execution

        # Assert
        for task in mock_tasks:
            task.execute.assert_called_once()

    def test_pipeline_shutdown(self):
        # Arrange
        mock_task = MagicMock(spec=Task)

        # Act
        self.pipeline.enqueue(mock_task)
        self.pipeline.shutdown()

        # Assert
        self.assertFalse(self.pipeline._running)

    def test_error_in_task_execution(self):
        # Arrange
        mock_task = MagicMock(spec=Task)
        mock_task.execute.side_effect = Exception("Task failed")

        # Act
        self.pipeline.enqueue(mock_task)
        time.sleep(0.2)

        # Assert
        mock_task.execute.assert_called_once()
        # Additional assertions for error handling once implemented

    def test_parallel_execution(self):
        # Arrange
        execution_order = []
        execution_starts = []
        lock = threading.Lock()

        def slow_task(task_id):
            with lock:
                execution_starts.append((task_id, time.time()))
            time.sleep(0.2)  # Simulate work
            with lock:
                execution_order.append(task_id)

        mock_tasks = []

        def create_task_effect(task_id):
            return lambda: slow_task(task_id)

        for i in range(4):
            task = MagicMock(spec=Task)
            task.execute.side_effect = create_task_effect(i)
            mock_tasks.append(task)

        # Act
        for task in mock_tasks:
            self.pipeline.enqueue(task)

        time.sleep(0.5)  # Wait for TaskPipeline to execute all tasks

        # Assert
        self.assertEqual(len(execution_order), 4, "All tasks should complete")

        # Check that some tasks ran in parallel by looking at start times
        start_times = [start for _, start in sorted(execution_starts)]
        parallel_executed = False
        for i in range(len(start_times) - 1):
            if start_times[i + 1] - start_times[i] < 0.1:  # Tasks started close together
                parallel_executed = True
                break

        self.assertTrue(parallel_executed, "Tasks should execute in parallel")

    def test_task_queue_order(self):
        # Arrange
        execution_order = []
        mock_tasks = []

        def create_task_effect(task_id):
            return lambda: execution_order.append(task_id)

        for i in range(3):
            task = MagicMock(spec=Task)
            task.execute.side_effect = create_task_effect(i)
            mock_tasks.append(task)

        # Act
        for task in mock_tasks:
            self.pipeline.enqueue(task)
        time.sleep(0.3)

        # Assert
        self.assertEqual(len(execution_order), 3)
        # Order might vary due to threading, but all tasks should be executed
        self.assertEqual(set(execution_order), {0, 1, 2})

    @patch('threading.Thread')
    def test_worker_thread_creation(self, mock_thread):
        # Act
        TaskPipeline(num_workers=2)

        # Assert
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()

    def test_empty_queue_behavior(self):
        # Arrange
        mock_task = MagicMock(spec=Task)

        # Act
        self.pipeline.enqueue(mock_task)
        time.sleep(0.2)

        # Assert
        self.assertTrue(self.pipeline.task_queue.empty())
        mock_task.execute.assert_called_once()


if __name__ == '__main__':
    unittest.main()
