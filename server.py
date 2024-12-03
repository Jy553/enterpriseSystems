from datetime import datetime
import pika
import time
import json
import random
from models.bill import Bill
from models.message import Message
from models.reading import Reading
from pydantic import ValidationError

def on_message_received(channel, method, properties, body):
    cost_per_unit = 1.30
   

    # Parse incoming payload
    try:
        data = Message[Reading].model_validate_json(body)
        if(data.messageType != 'READING'):
            print("invalid message type")
            return
        
        cost = (data.data.reading_value * cost_per_unit)
        
        print(f"ID: {data.data.meter_id} | Usage: {data.data.reading_value}{data.data.reading_unit}")


        response = Message[Bill](
            messageType='BILL',
            data=Bill(
                consumption=data.data.reading_value,
                consumption_cost=cost,
                meter_id=data.data.meter_id,
                total_bill=cost,
                cost_per_unit=cost_per_unit,
                is_initial_reading=False,
                billing_period=12,
                billing_period_start=datetime.now(),
                billing_period_end=datetime.now(),
                total_standing_charge=cost
            ))
        
        print(response.model_dump_json());

        channel.basic_publish('', routing_key=properties.reply_to,
                          body=response.model_dump_json(), properties=pika.BasicProperties(correlation_id=properties.correlation_id))
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except ValidationError as e:
        print(f"Invalid payload: {properties.correlation_id}")
    except Exception as e:
        print("Error")




connection_parameters = pika.ConnectionParameters('localhost')

connection = pika.BlockingConnection(connection_parameters)

channel = connection.channel()

channel.queue_declare(queue='readings')

# Controls the number of messages it can process at a time. 
channel.basic_qos(prefetch_count=1)

channel.basic_consume(queue='readings', on_message_callback=on_message_received)

print("Starting consuming")

channel.start_consuming()