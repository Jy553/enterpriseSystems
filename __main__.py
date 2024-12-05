import sys
from typing import Optional
import pika
from client.api_handler import ApiHandler
from models.task_communications_data import TaskCommunicationsData
from server.api.tasks.deserialization.task_deserialize_reading import TaskDeserializeReading
from server.task_pipeline.task_pipeline import TaskPipeline
from server.task_pipeline.task_manager import TaskManager
from server.config import Config


class Server:
    def __init__(self):
        self.task_pipeline: Optional[TaskPipeline] = None

    def initialize(self) -> None:
        """Initialize all server components."""
        try:
            print("Initializing server components...")

            self.task_pipeline = TaskPipeline(num_workers=4)
            TaskManager.initialize(self.task_pipeline)

            Config.initialize(
                price_per_unit=0.20,  # £0.20 per kWh
                standing_charge=0.25  # £0.25 per day
            )

            print("Server initialization completed successfully")

        except Exception as e:
            print(f"Error during server initialization: {str(e)}")
            raise


def main() -> None:
    """Main entry point for the server application."""
    server = Server()
    api_handler = ApiHandler()

    try:
        server.initialize()
        print("\nServer is running.")
        api_handler.connect()

        def on_message_received_reading_queue(channel, method, properties, body):

            print("Message received")
            communications_data = TaskCommunicationsData()
            communications_data.channel = channel
            communications_data.method = method
            communications_data.properties = properties
            communications_data.body = body

            print("Attempt to enqueue message")
            TaskManager.enqueue(TaskDeserializeReading(
                reading_json=body,
                communication_data=communications_data))

            channel.basic_ack(delivery_tag=method.delivery_tag)
            print("Message enqueued and acknowledged")
        connection_parameters = pika.ConnectionParameters('localhost')

        connection = pika.BlockingConnection(connection_parameters)

        channel = connection.channel()

        channel.queue_declare(
            queue='readings')

        channel.basic_consume(
            queue='readings',
            on_message_callback=on_message_received_reading_queue)

        print("Starting consuming")

        channel.start_consuming()

        while True:

            pass

    except Exception as e:
        print(f"Critical error in server main: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
