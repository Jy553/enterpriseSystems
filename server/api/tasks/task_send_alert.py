import pika

from models.task import Task


class TaskSendAlert(Task):
    def __init__(self, meter_id: str, alert_message: str, communication_data):
        self.meter_id = meter_id
        self.alert_message = alert_message
        self.communication_data = communication_data

    def execute(self) -> None:
        method = self.communication_data.method
        properties = self.communication_data.properties

        connection_parameters = pika.ConnectionParameters('localhost')

        connection = pika.BlockingConnection(connection_parameters)

        channel = connection.channel()

        channel.basic_publish(
            '',
            routing_key=properties.reply_to,
            body=self.alert_message,
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id))
        channel.basic_ack(delivery_tag=method.delivery_tag)
