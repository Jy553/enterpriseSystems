import time
from abc import ABC, abstractmethod
import uuid


class Task(ABC):
    def __init__(self, task_info, is_priority=False):
        self.task_id = str(uuid.uuid4())
        self.task_info = task_info
        self.is_disposed = False
        self.is_priority = is_priority
        self.last_execution_attempt = time.time()
        self.attempts = 0

    @abstractmethod
    def execute(self):
        pass

    def dispose(self):
        self.is_disposed = True

    def __str__(self):
        return f"{self.__class__.__name__}(task_id={self.task_id}, task_info={self.task_info})"
