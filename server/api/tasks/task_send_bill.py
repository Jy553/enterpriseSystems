import pika

from models.task import Task


class TaskSendBill(Task):
    def __init__(self, bill_json: str, communication_data):
        self.bill_json = bill_json
        self.communication_data = communication_data

    def execute(self):
        method = self.communication_data.method
        properties = self.communication_data.properties

        connection_parameters = pika.ConnectionParameters('localhost')

        connection = pika.BlockingConnection(connection_parameters)

        channel = connection.channel()

        channel.basic_publish(
            '',
            routing_key=properties.reply_to,
            body=self.bill_json,
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id))
        channel.basic_ack(delivery_tag=method.delivery_tag)
