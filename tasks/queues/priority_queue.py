import time
from queue import PriorityQueue as _PriorityQueue


class PriorityQueue(_PriorityQueue):
    def __init__(self, maxsize=0):
        super().__init__(maxsize=maxsize)
        self.counter = 0

    def put(self, item, block=True, timeout=None):
        priority = 0 if item.is_priority else 1
        self.counter += 1
        super().put((priority, self.counter, item), block, timeout)

    def get(self, block=True, timeout=None):
        _, _, item = super().get(block, timeout)
        return item
