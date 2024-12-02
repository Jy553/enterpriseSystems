import pika
import time
import json
import random

def on_message_received(channel, method, properties, body):
    processing_time = random.randint(1,6)
    
    try: 
        print(f"received body: {body}, will take {processing_time}s to process")
        time.sleep(processing_time)
        channel.basic_ack(delivery_tag=method.delivery_tag)
        message = json.loads(body)
        message_id = message.get('id', 'N/A')
        print(f"Message {message_id} processed")
    except json.JSONDecodeError:
        print("Failed to decode message body. Skipping message.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally: 
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