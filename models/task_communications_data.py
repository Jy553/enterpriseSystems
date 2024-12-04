from dataclasses import dataclass


@dataclass
class TaskCommunicationsData:
    def __init__(self):
        channel: str
        method: str
        properties: str
        body: str
