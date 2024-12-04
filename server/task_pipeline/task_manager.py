import threading
from typing import Optional
from models.task import Task
from server.task_pipeline.task_pipeline import TaskPipeline


class TaskManager:
    _instance = None
    _lock = threading.Lock()
    _pipeline: Optional[TaskPipeline] = None

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TaskManager, cls).__new__(cls)
            return cls._instance

    @classmethod
    def initialize(cls, pipeline: TaskPipeline) -> None:
        with cls._lock:
            if cls._pipeline is not None:
                raise RuntimeError("TaskManager already initialized")
            cls._pipeline = pipeline

    @classmethod
    def enqueue(cls, task: Task) -> None:
        if cls._pipeline is None:
            raise RuntimeError("TaskManager not initialized")
        cls._pipeline.enqueue(task)
