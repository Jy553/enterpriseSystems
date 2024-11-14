import pika
import time
import json
import random

def on_message_received(channel, method, properties, body):
    processing_time = random.randint(1,6)
    
    print(f"received body: {body}, will take {processing_time}s to process")
    time.sleep(processing_time)
    channel.basic_ack(delivery_tag=method.delivery_tag)
    print(f"Message {json.loads(body)['id']} processed")


connection_parameters = pika.ConnectionParameters('localhost')

connection = pika.BlockingConnection(connection_parameters)

channel = connection.channel()

channel.queue_declare(queue='readings')

# Controls the number of messages it can process at a time. 
channel.basic_qos(prefetch_count=1)

channel.basic_consume(queue='readings', on_message_callback=on_message_received)

print("Starting consuming")

channel.start_consuming()