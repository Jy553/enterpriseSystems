"""
Author: Liam McClelland
Date: 10/11/2024

Description:
    This class manages the interactions with a RabbitMQ queue, providing methods to connect, send messages, and consume messages from the queue using a callback function.
    This is designed for use in enterprise grade applications, with exception handling, logging, and context management to ensure robust resource handling and traceability. 
"""

import uuid
import pika
from pika import exceptions
import logging


class ApiHandler:
    """Handles interaction with RabbitMQ for sending and receiving messages across multiple queues."""

    def __init__(self, host="localhost"):
        """
        Initializes the ApiHandler with a specified RabbitMQ host.

        Parameters:
        - host (str): Hostname of the RabbitMQ server.
        """
        self.host = host
        self.connection = None
        self.channel = None
        self.reply_queue = None

    def connect(self):
        """Establishes a connection to RabbitMQ and initializes the channel."""
        try:
            # Attempt to connect to RabbitMQ
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
            self.channel = self.connection.channel()
            logging.info(f"Connected to RabbitMQ on host {self.host}")
        except pika.exceptions.AMQPConnectionError as e:
            logging.error(f"Failed to connect to RabbitMQ: {str(e)}")
            self.close()
            raise ConnectionError()

    def declare_queue(self, queue_name):
        """
        Declares a RabbitMQ queue.

        Parameters:
        - queue_name (str): Name of the queue to declare.
        """
        try:
            if self.channel and self.connection.is_open:
                # Declare the queue (idempotent operation)
                self.channel.queue_declare(queue=queue_name)
                logging.info(f"Declared queue: {queue_name}")
            else:
                logging.warning("No active RabbitMQ channel.")
        except Exception as e:
            logging.error(f"Failed to declare queue '{queue_name}': {str(e)}")

    def declare_reply_queue(self):
        try:
            if self.reply_queue != None:
                return self.reply_queue
        
            if self.channel and self.connection.is_open:
                self.reply_queue = self.channel.queue_declare(queue='', exclusive=True)

        except Exception as e:
            logging.error(f"Failed to declare reply queue {str(e)}'")
            return None

        return self.reply_queue;
            

    def send_message(self, queue_name, message):
        """
        Sends a message to the specified RabbitMQ queue.

        Parameters:
        - queue_name (str): The name of the queue to send the message to.
        - message (str): The message to send to the queue.
        """
        try:
            cor_id = str(uuid.uuid4())

            # Ensure the channel is open and valid
            if not self.connection.is_open or not self.channel.is_open:
                logging.error("Connection or channel is closed. Reconnecting...")
                self.connect()
                self.declare_reply_queue()  # Re-declare the reply-to queue after reconnecting
                self.channel = self.connection.channel()  # Re-create the channel


            if self.channel and self.connection.is_open:
                self.channel.basic_publish(exchange='', 
                        routing_key='readings',
                        body=message, 
                        properties=pika.BasicProperties(
                            content_type='application/json',
                            correlation_id=cor_id,
                            reply_to=self.declare_reply_queue().method.queue
                        )  # Set the content type to JSON
                )
                logging.info(f"Sent message to queue '{queue_name}': {message}")
            else:
                logging.warning("No active RabbitMQ channel.")

        except pika.exceptions.StreamLostError as e:
           logging.error(f"Stream connection lost: {e}")
           self.connect()
           self.send_message(queue_name, message)  # Retry sending the message

        except Exception as e:
            logging.error(f"Failed to send message to queue '{queue_name}': {str(e)}")

    def receive_message(self, queue_name, callback):
        """
        Starts consuming messages from the specified RabbitMQ queue and passes each message to a callback.

        Parameters:
        - queue_name (str): The name of the queue to receive messages from.
        - callback (function): A function to process received messages.
        """
        try:

            # Ensure the channel is open and valid
            if not self.connection.is_open or not self.channel.is_open:
                logging.error("Connection or channel is closed. Reconnecting...")
                self.connect()
                self.declare_reply_queue()  # Re-declare the reply-to queue after reconnecting
                self.channel = self.connection.channel()  # Re-create the channel


            if self.channel and self.connection.is_open:
                def on_message(ch, method, properties, body):
                    
                    # Decode message and pass to the callback
                    decoded_message = body.decode()
                    logging.info(f"Received message from '{queue_name}': {decoded_message}")
                    callback(decoded_message)
                    ch.basic_ack(delivery_tag=method.delivery_tag)

                # Start consuming messages from the specified queue
                self.channel.basic_consume(queue=queue_name, on_message_callback=on_message)
                logging.info(f"Waiting for messages on queue '{queue_name}'...")
                self.connection.process_data_events(time_limit=1)
            else:
                logging.warning("No active RabbitMQ channel.")
        except IndexError as e:
           print(f"IndexError caught: {e} - Queue might be empty.")
           self.receive_message(queue_name, callback)  # Retry receiving messages
        except pika.exceptions.StreamLostError as e:
            logging.error(f"Stream connection lost: {e}")
            self.connect()  # Reconnect and reattempt
            self.declare_reply_queue()
            self.receive_message(queue_name, callback)  # Retry receiving messages
        except Exception as e:
            logging.error(f"Failed to receive message from queue '{queue_name}': {str(e)}")

    def receive_direct_replies(self, callback):
        self.receive_message(self.declare_reply_queue().method.queue, callback)

    def close(self):
        """Closes the connection to RabbitMQ, ensuring a clean disconnect."""
        if self.connection:
            try:
                self.connection.close()
                logging.info("Closed RabbitMQ connection")
            except Exception as e:
                logging.error(f"Failed to close RabbitMQ connection: {str(e)}")

    def __enter__(self):
        """Allows the ApiHandler to be used as a context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensures the connection is closed when exiting the context."""
        self.close()


if __name__ == "__main__":
    handler = ApiHandler();

    #handler.send_message('test message')

    def handleReply(message):
        print(f"Received: {message}")

    handler.receive_message(queue_name='updates', callback=handleReply);
    print('test')