import json
import pika
import random
import time
import uuid
from pika.exchange_type import ExchangeType


def reply_callback_received(channel, method, properties, body):
    print(f'reply received for: {properties.correlation_id}')

connection_parameters = pika.ConnectionParameters('localhost')

connection = pika.BlockingConnection(connection_parameters)

channel = connection.channel()
reply_queue = channel.queue_declare(queue='', exclusive=True)

channel.basic_consume(queue=reply_queue.method.queue, auto_ack=True, on_message_callback=reply_callback_received)

messageId = 1

for x in range(3):
    cor_id = str(uuid.uuid4())
    message = {
    "id": f"{messageId}",
    "usage": f"{random.randint(1,100)}.{random.randint(1,99)}kwh"
}
    channel.basic_publish(exchange='', 
                        routing_key='readings',
                        body=json.dumps(message), 
                        properties=pika.BasicProperties(
                            content_type='application/json',
                            correlation_id=cor_id,
                            reply_to=reply_queue.method.queue
                        )  # Set the content type to JSON
)

    print(f"sent message: {message}")

    time.sleep(random.randint(1,4))

    messageId+=1

channel.start_consuming()
    

