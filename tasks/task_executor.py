import time
import logging
import threading
from queue import Empty


class TaskExecutor:
    def __init__(self, normal_queue, priority_queue, logger=None, priority_boost_threshold=60, max_attempts=3):
        self.normal_queue = normal_queue
        self.priority_queue = priority_queue
        self.logger = logger or logging.getLogger(__name__)
        self.priority_boost_threshold = priority_boost_threshold
        self.running = False
        self.thread = None
        self.max_attempts = max_attempts

    def execute_next_task(self):
        task = self.get_next_task()
        if task:
            self.process_task(task)
        return task

    def get_next_task(self):
        try:
            return self.get_priority_task()
        except Empty:
            return self.get_normal_task()

    def get_priority_task(self):
        return self.priority_queue.get(block=False)

    def get_normal_task(self):
        try:
            task = self.normal_queue.get(block=False)
            if self.should_boost_priority(task):
                self.boost_task_priority(task)
                return self.get_next_task()  # Retry from the beginning
            return task
        except Empty:
            self.logger.info("No tasks available")
            raise Empty("No tasks available")

    def should_boost_priority(self, task):
        return time.time() - task.last_execution_attempt > self.priority_boost_threshold

    def boost_task_priority(self, task):
        self.logger.info(f"Boosting priority for task: {task}")
        self.priority_queue.put(task)

    def process_task(self, task):
        task.last_execution_attempt = time.time()
        self.logger.info(
            f"Executing task: {task.__class__.__name__}(task_id={task.task_id}, task_info={task.task_info})")
        try:
            task.execute()
            self.logger.info(f"Task executed successfully: {task}")
        except Exception as e:
            self.handle_task_error(task, e)

    def handle_task_error(self, task, exception):
        error_message = f"Error executing task: {str(exception)}"
        self.logger.error(error_message)

        if not hasattr(task, 'attempts'):
            task.attempts = 0
        task.attempts += 1

        if task.attempts < self.max_attempts:
            self.logger.info(f"Retrying task (attempt {task.attempts}/{self.max_attempts})")
            self.normal_queue.put(task)  # Put the task back in the normal queue for retry
        else:
            self.logger.error(f"Task failed after {self.max_attempts} attempts: {task}")
            # TODO: Consider implementing a dead-letter queue for tasks that have failed after max attempts

    def run(self, max_tasks=None):
        self.running = True
        tasks_executed = 0
        while self.running and (max_tasks is None or tasks_executed < max_tasks):
            try:
                self.execute_next_task()
                tasks_executed += 1
            except Empty:
                self.logger.info("No tasks available, sleeping...")
                time.sleep(1)
                if max_tasks is not None:
                    tasks_executed += 1

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def run_in_thread(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        return self.thread
