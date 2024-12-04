import json
import pika
import random
import time
import uuid
from pika.exchange_type import ExchangeType
from client.models.message import Message
from models.reading import Reading


def reply_callback_received(channel, method, properties, body):
    print(f'reply received for: {properties.correlation_id}')
    print(f'body: {body}')


connection_parameters = pika.ConnectionParameters('localhost')

connection = pika.BlockingConnection(connection_parameters)

channel = connection.channel()
reply_queue = channel.queue_declare(queue='', exclusive=True)
channel.queue_declare(queue='readings')

channel.basic_consume(queue=reply_queue.method.queue, auto_ack=True, on_message_callback=reply_callback_received)

messageId = 1

for x in range(3):
    cor_id = str(uuid.uuid4())
    message = Message[Reading](
        messageType="READING",
        data=Reading(
            meter_id="id12783612",
            reading_value=random.randint(1, 100)
        ),
    )
    channel.basic_publish(exchange='',
                          routing_key='readings',
                          body=message.model_dump_json(),
                          properties=pika.BasicProperties(
                              content_type='application/json',
                              correlation_id=cor_id,
                              reply_to=reply_queue.method.queue
                          )  # Set the content type to JSON
                          )

    print(f"sent message: {message}")

    time.sleep(random.randint(1, 4))

    messageId += 1

channel.start_consuming()
