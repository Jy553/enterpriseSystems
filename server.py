import pika
import time
import json
import random

def on_message_received(channel, method, properties, body):
    print(f"Request received: {properties.correlation_id}")
    channel.basic_publish('', routing_key=properties.reply_to,
                          body=f'Replying to {properties.correlation_id}', properties=pika.BasicProperties(correlation_id=properties.correlation_id))
    channel.basic_ack(delivery_tag=method.delivery_tag)




connection_parameters = pika.ConnectionParameters('localhost')

connection = pika.BlockingConnection(connection_parameters)

channel = connection.channel()

channel.queue_declare(queue='readings')

# Controls the number of messages it can process at a time. 
channel.basic_qos(prefetch_count=1)

channel.basic_consume(queue='readings', on_message_callback=on_message_received)

print("Starting consuming")

channel.start_consuming()