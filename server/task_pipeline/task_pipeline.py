import queue
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from models.task import Task
import threading
import logging


class TaskPipeline:
    def __init__(self, num_workers: int = 4):
        self.task_queue = Queue()
        self.thread_pool = ThreadPoolExecutor(max_workers=num_workers)
        self._running = True
        self.worker_thread = threading.Thread(target=self._process_queue)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        print(f"TaskPipeline initialized with {num_workers} workers")

    def enqueue(self, task: Task) -> None:
        print(f"\n=== Enqueueing Task: {task.__class__.__name__} ===")
        self.task_queue.put(task)
        print("Task added to queue successfully")

    def _process_queue(self) -> None:
        print("Starting task processing loop")
        while self._running:
            try:
                # Get task with timeout to allow checking running flag
                task = self.task_queue.get(timeout=1.0)
                print(f"\n=== Processing Task: {task.__class__.__name__} ===")

                # Submit task to thread pool
                future = self.thread_pool.submit(task.execute)

                # Wait for task completion and handle any errors
                try:
                    future.result()  # This will raise any exceptions from the task
                    print(f"Task completed successfully: {task.__class__.__name__}")
                except Exception as e:
                    print(f"Error executing task {task.__class__.__name__}: {str(e)}")
                finally:
                    self.task_queue.task_done()

            except queue.Empty:
                continue  # No tasks available, continue waiting
            except Exception as e:
                print(f"Error in task processing loop: {str(e)}")

    def shutdown(self) -> None:
        print("Shutting down TaskPipeline")
        self._running = False
        self.worker_thread.join()
        self.thread_pool.shutdown()
        print("TaskPipeline shutdown complete")