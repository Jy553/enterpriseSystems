from exceptions.scheduler_error import SchedulerError
from tasks.concrete_tasks.alert_task import AlertTask
import logging
from queue import Full


class TaskScheduler:
    def __init__(self, normal_queue, priority_queue, priority_checker=None, logger=None):
        self.normal_queue = normal_queue
        self.priority_queue = priority_queue
        self.priority_checker = priority_checker or self._default_priority_checker
        self.logger = logger or logging.getLogger(__name__)

    def schedule(self, task):
        try:
            if self.priority_checker(task):
                self.priority_queue.put(task, block=False)
                self.logger.info(f"Scheduled priority task {task.task_id} to priority queue")
            else:
                self.normal_queue.put(task, block=False)
                self.logger.info(f"Scheduled task {task.task_id} to normal queue")
        except Full:
            self.logger.error(f"Failed to schedule task {task.task_id}. Queue is full.")
            raise SchedulerError(f"Queue is full. Cannot schedule task {task.task_id}")

    @staticmethod
    def _default_priority_checker(task):
        return isinstance(task, AlertTask) or task.is_priority
