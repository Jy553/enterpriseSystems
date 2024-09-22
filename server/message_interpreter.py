class MessageInterpreter:
    def __init__(self, task_factory):
        self.task_factory = task_factory

    def interpret(self, message):
        task_type = message.get('type')
        task_info = message.get('data')

        if not task_type or not task_info:
            raise ValueError("Invalid message format")

        return self.task_factory.create_task(task_type, task_info)