import threading
import queue
import time
import uuid
import pika
from pika import exceptions
import logging
from typing import Callable


class MessagingClient:
    """
    Handles RabbitMQ messaging with separate threads for sending and receiving messages.
    Uses a single connection with separate channels for publishing and consuming.
    """

    def __init__(self, host: str = "localhost"):
        self.host = host
        self.connection = None
        self.publish_channel = None
        self.consume_channel = None
        self.reply_queue = None
        self.callback_queue = queue.Queue()
        self.response_callbacks = {}
        self.running = False
        self.consumer_thread = None

    def connect(self) -> bool:
        """Establishes connection and creates channels."""
        try:
            # Create the main connection
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host))

            # Create separate channels for publishing and consuming
            self.publish_channel = self.connection.channel()
            self.consume_channel = self.connection.channel()

            # Declare the reply queue
            self.reply_queue = self.consume_channel.queue_declare(queue='', exclusive=True)

            # Start the consumer thread
            self.running = True
            self.consumer_thread = threading.Thread(target=self._consume_responses)
            self.consumer_thread.daemon = True
            self.consumer_thread.start()

            logging.info("Successfully connected to RabbitMQ")
            return True

        except Exception as e:
            logging.error(f"Failed to connect to RabbitMQ: {e}")
            self.close()
            return False

    def _consume_responses(self):
        """Consumer thread that handles incoming messages."""

        def callback(ch, method, props, body):
            try:
                correlation_id = props.correlation_id
                if correlation_id in self.response_callbacks:
                    callback_func = self.response_callbacks[correlation_id]
                    callback_func(body.decode())
                    del self.response_callbacks[correlation_id]
            except Exception as e:
                logging.error(f"Error processing response: {e}")
            finally:
                ch.basic_ack(delivery_tag=method.delivery_tag)

        try:
            self.consume_channel.basic_consume(
                queue=self.reply_queue.method.queue,
                on_message_callback=callback
            )

            while self.running:
                try:
                    # Process messages with a timeout to allow checking running flag
                    self.connection.process_data_events(time_limit=1)
                except pika.exceptions.AMQPError as e:
                    logging.error(f"AMQP error in consumer: {e}")
                    self._handle_connection_error()
                    break
        except Exception as e:
            logging.error(f"Consumer thread error: {e}")

    def _handle_connection_error(self):
        """Handles connection errors by attempting to reconnect."""
        while self.running:
            try:
                self.close()
                if self.connect():
                    break
            except Exception as e:
                logging.error(f"Reconnection attempt failed: {e}")
            time.sleep(5)  # Wait before retrying

    def send_message(self, queue: str, message: str, callback: Callable[[str], None]) -> bool:
        """
        Sends a message to specified queue and registers callback for response.

        Args:
            queue: Queue to send message to
            message: Message content
            callback: Function to call with response

        Returns:
            bool: True if message was sent successfully
        """
        try:
            if not self.connection or not self.connection.is_open:
                if not self.connect():
                    return False

            correlation_id = str(uuid.uuid4())
            self.response_callbacks[correlation_id] = callback

            self.publish_channel.basic_publish(
                exchange='',
                routing_key=queue,
                body=message,
                properties=pika.BasicProperties(
                    content_type='application/json',
                    correlation_id=correlation_id,
                    reply_to=self.reply_queue.method.queue
                )
            )
            return True
        except Exception as e:
            logging.error(f"Error sending message: {e}")
            return False

    def close(self):
        """Closes all connections and channels."""
        self.running = False
        try:
            if self.publish_channel:
                self.publish_channel.close()
            if self.consume_channel:
                self.consume_channel.close()
            if self.connection:
                self.connection.close()
        except Exception as e:
            logging.error(f"Error closing connections: {e}")
        finally:
            self.publish_channel = None
            self.consume_channel = None
            self.connection = None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()