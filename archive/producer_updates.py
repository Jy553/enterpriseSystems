import json
import pika
import random
import time
from pika.exchange_type import ExchangeType

connection_parameters = pika.ConnectionParameters('localhost')

connection = pika.BlockingConnection(connection_parameters)

channel = connection.channel()
channel.exchange_declare(exchange="notifications", exchange_type=ExchangeType.fanout)

messageId = 1


while(True):
    message = {
    "id": f"{messageId}",
    "usage": f"{random.randint(1,100)}.{random.randint(1,99)}kwh"
}
    channel.basic_publish(exchange='', routing_key='readings', body=json.dumps(message), properties=pika.BasicProperties(content_type='application/json')  # Set the content type to JSON
)

    print(f"sent message: {message}")

    time.sleep(random.randint(1,4))

    messageId+=1

    

