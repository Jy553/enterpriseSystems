"""
Author: Liam McClelland
Date: 10/11/2024

Description:
    This class manages the interactions with a RabbitMQ queue, providing methods to connect, send messages, and consume messages from the queue using a callback function.
    This is designed for use in enterprise grade applications, with exception handling, logging, and context management to ensure robust resource handling and traceability. 
"""

import pika
import logging


class ApiHandler:
    """Handles interaction with a RabbitMQ queue for sending and receiving messages related to smart meter data."""

    def __init__(self, queue_name="smart_meter_queue", host="localhost"):
        """
        Initializes the ApiHandler with a specified RabbitMQ queue and host.

        Parameters:
        - queue_name (str): Name of the RabbitMQ queue to interact with.
        - host (str): Hostname of the RabbitMQ server.
        """
        self.queue_name = queue_name
        self.host = host
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        """Establishes a connection to RabbitMQ and declares the queue."""
        try:
            # Attempt to connect to RabbitMQ
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
            self.channel = self.connection.channel()
            
            # Declare the queue (idempotent operation)
            self.channel.queue_declare(queue=self.queue_name)
            logging.info(f"Connected to RabbitMQ on host {self.host}, queue: {self.queue_name}")
        except pika.exceptions.AMQPConnectionError as e:
            logging.error(f"Failed to connect to RabbitMQ: {str(e)}")
            self.close()

    def send_message(self, message):
        """
        Sends a message to the specified RabbitMQ queue.

        Parameters:
        - message (str): The message to send to the queue.
        """
        try:
            if self.channel and self.connection.is_open:
                self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=message)
                logging.info(f"Sent message to queue '{self.queue_name}': {message}")
            else:
                logging.warning("No active RabbitMQ channel.")
        except Exception as e:
            logging.error(f"Failed to send message: {str(e)}")

    def receive_message(self, callback):
        """
        Starts consuming messages from the RabbitMQ queue and passes each message to a callback.

        Parameters:
        - callback (function): A function to process received messages.
        """
        try:
            if self.channel and self.connection.is_open:
                def on_message(ch, method, properties, body):
                    # Decode message and pass to the callback
                    decoded_message = body.decode()
                    logging.info(f"Received message: {decoded_message}")
                    callback(decoded_message)
                    ch.basic_ack(delivery_tag=method.delivery_tag)

                # Start consuming messages
                self.channel.basic_consume(queue=self.queue_name, on_message_callback=on_message)
                logging.info("Waiting for messages...")
                self.channel.start_consuming()
            else:
                logging.warning("No active RabbitMQ channel.")
        except Exception as e:
            logging.error(f"Failed to receive message: {str(e)}")

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
