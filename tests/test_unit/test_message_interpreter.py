import unittest
from server.message_interpreter import MessageInterpreter
from tasks.concrete_tasks.meter_reading_task import MeterReadingTask
from tasks.task_factory import TaskFactory


class TestMessageInterpreter(unittest.TestCase):
    def setUp(self):
        self.factory = TaskFactory()
        self.interpreter = MessageInterpreter(self.factory)

    def test_interpret_meter_reading_message(self):
        message = {"type": "meter_reading", "data": {"meter_id": "123", "reading": 100}}
        task = self.interpreter.interpret(message)
        self.assertIsInstance(task, MeterReadingTask)

    def test_interpret_invalid_message(self):
        with self.assertRaises(ValueError):
            self.interpreter.interpret({"invalid": "message"})
