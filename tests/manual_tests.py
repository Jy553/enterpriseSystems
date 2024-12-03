import time
from typing import Set

# Client-side imports
from client.business_logic.meter_client import MeterClient
from client.api.meter_reading_serializer import MeterReadingSerializer

# Server-side imports
from server.mock_memory.mock_readings_memory import MockReadingsMemory
from server.api.meter_reading_deserializer import MeterReadingDeserializer
from server.business_logic.tasks.calculate_bill.task_calculate_bill import TaskCalculateBill
from server.task_pipeline.task_pipeline import TaskPipeline


def test_system():
    print("Starting system test...\n")

    # Initialize components
    print("Initializing components...")

    # Server-side components
    server_storage = MockReadingsMemory()
    task_pipeline = TaskPipeline(num_workers=2)

    # Price configuration
    PRICE_PER_UNIT = 0.20  # £0.20 per kWh
    STANDING_CHARGE = 0.25  # £0.25 per day

    print("Server components initialized")
    print(f"Price per unit: £{PRICE_PER_UNIT:.2f}/kWh")
    print(f"Standing charge: £{STANDING_CHARGE:.2f}/day\n")

    # Client-side components
    client = MeterClient()
    client.min_delay = 5  # Reduce delay for testing
    client.max_delay = 10

    print("Client components initialized")
    print("Using shortened delays (5-10 seconds) for testing\n")

    # Keep track of processed readings
    processed_message_ids: Set[str] = set()

    try:
        # Start client
        print("Starting client...")
        client.start()

        # Process a few readings
        readings_processed = 0
        max_readings = 3

        while readings_processed < max_readings:
            # Wait for new reading in client memory
            latest_reading = client.memory.get_latest_reading()

            if latest_reading is None or latest_reading.message_id in processed_message_ids:
                time.sleep(1)
                continue

            # Process the new reading
            processed_message_ids.add(latest_reading.message_id)

            # Get the JSON that would be sent to RabbitMQ
            reading_json = MeterReadingSerializer.to_json(latest_reading)
            print("\n=== Received new reading from client (via mock RabbitMQ) ===")
            print(f"Message ID: {latest_reading.message_id}")
            print(f"Meter ID: {latest_reading.meter_id}")
            print(f"Reading Value: {latest_reading.reading_value:.2f} {latest_reading.reading_unit}")
            print(f"Sequence Number: {latest_reading.sequence_number}")
            print(f"Timestamp: {latest_reading.timestamp}")
            print("\nJSON payload:")
            print(reading_json)

            # Server-side processing
            print("\n=== Server processing starting ===")

            try:
                # Deserialize the reading
                deserialized_reading = MeterReadingDeserializer.from_json(reading_json)
                print("Reading deserialized successfully")

                # Create and enqueue billing task
                billing_task = TaskCalculateBill(
                    reading=deserialized_reading,
                    storage=server_storage,
                    price_per_unit=PRICE_PER_UNIT,
                    standing_charge=STANDING_CHARGE
                )

                # Execute task directly for testing
                print("\n=== Billing calculation results ===")
                bill_json = billing_task.execute()
                print(bill_json)

                readings_processed += 1
                print(f"\nProcessed reading {readings_processed}/{max_readings}")

                if readings_processed < max_readings:
                    print("\nWaiting for next reading...")

            except Exception as e:
                print(f"\nError processing reading: {str(e)}")
                # Don't count failed readings
                processed_message_ids.remove(latest_reading.message_id)

        print("\nTest completed successfully!")

    except Exception as e:
        print(f"\nError during test: {str(e)}")
    finally:
        # Cleanup
        print("\nShutting down components...")
        client.stop()
        task_pipeline.shutdown()
        print("Test cleanup completed")


if __name__ == "__main__":
    test_system()
