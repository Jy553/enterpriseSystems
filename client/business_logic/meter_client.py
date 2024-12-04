import random
import threading
import time
from typing import Optional
from client.business_logic.reading_generator import ReadingGenerator
from client.mock_memory.client_mock_memory import ClientMockMemory
from client.api.meter_reading_serializer import MeterReadingSerializer


class MeterClient:
    def __init__(self):
        self._meter_id = "METER_" + str(random.randint(1000, 9999))  # Client owns the meter ID
        self.generator = ReadingGenerator()
        self.memory = ClientMockMemory()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.min_delay = 15  # minimum delay in seconds
        self.max_delay = 60  # maximum delay in seconds

    def start(self):
        """Start the client's reading generation process."""
        if self._running:
            print("Client is already running")
            return

        self._running = True
        self._thread = threading.Thread(target=self._generation_loop)
        self._thread.daemon = True  # Allow the program to exit even if thread is running
        self._thread.start()
        print(f"Client started with meter ID: {self._meter_id}")

    def stop(self):
        """Stop the client's reading generation process."""
        if not self._running:
            print("Client is not running")
            return

        self._running = False
        if self._thread:
            self._thread.join()
            self._thread = None
        print("Client stopped")

    def _generation_loop(self):
        """Main loop for generating and saving readings."""
        while self._running:
            try:
                # Generate new reading with our meter ID
                reading = self.generator.generate_reading(self._meter_id)

                # Save reading
                self.memory.save_new_meter_reading(reading.message_id, reading)

                # Serialize reading for RabbitMQ
                reading_json = MeterReadingSerializer.to_json(reading)

                # Print reading information
                print(f"\nNew Reading Generated at {reading.timestamp}:")
                print(f"Meter ID: {reading.meter_id}")
                print(f"Reading Value: {reading.reading_value:.2f} {reading.reading_unit}")
                print(f"Sequence Number: {reading.sequence_number}")
                print(f"Message ID: {reading.message_id}")
                if reading.previous_reading is not None:
                    print(
                        f"Difference from previous: {reading.reading_value - reading.previous_reading:.2f} {reading.reading_unit}")

                print("\nJSON for RabbitMQ:")
                print(reading_json)

                # Calculate random delay for next reading
                delay = random.uniform(self.min_delay, self.max_delay)
                print(f"\nNext reading in {delay:.1f} seconds...")

                # Break the delay into smaller chunks to allow for clean shutdown
                chunks = int(delay * 2)  # Split into half-second chunks
                chunk_size = delay / chunks

                for _ in range(chunks):
                    if not self._running:
                        return
                    time.sleep(chunk_size)

            except Exception as e:
                print(f"Error in generation loop: {e}")
                time.sleep(5)  # Wait a bit before retrying


def main():
    """Manual testing function"""
    client = MeterClient()

    try:
        client.start()

        # Keep the main thread alive
        while True:
            cmd = input("\nEnter 'q' to quit: ").lower()
            if cmd == 'q':
                break

    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt")
    finally:
        client.stop()
        print("Client shutdown complete")


if __name__ == "__main__":
    main()