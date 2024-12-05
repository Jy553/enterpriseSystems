from abc import ABC, abstractmethod
from models.task_communications_data import TaskCommunicationsData


class Task(ABC):

    def __init(self,
               task_communications_data: TaskCommunicationsData):
        self.task_communications_data = task_communications_data

    @abstractmethod
    def execute(self) -> None:
        pass
