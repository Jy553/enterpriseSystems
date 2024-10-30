import queue
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from tasks.task import Task
import threading


class TaskPipeline:
    def __init__(self, num_workers: int = 4):
        self.task_queue = Queue()
        self.thread_pool = ThreadPoolExecutor(max_workers=num_workers)
        self._running = True
        self.worker_thread = threading.Thread(target=self._process_queue)
        self.worker_thread.start()

    def enqueue(self, task: Task) -> None:
        self.task_queue.put(task)

    def _process_queue(self) -> None:
        while self._running:
            try:
                task = self.task_queue.get(timeout=1.0)
                self.thread_pool.submit(task.execute)
            except queue.Empty:
                continue

    def shutdown(self) -> None:
        self._running = False
        self.worker_thread.join()
        self.thread_pool.shutdown()