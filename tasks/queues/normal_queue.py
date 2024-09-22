from queue import Queue, PriorityQueue as _PriorityQueue


class NormalQueue(Queue):
    def __init__(self, maxsize=0):
        super().__init__(maxsize=maxsize)