import sys
from typing import Optional
from server.task_pipeline.task_pipeline import TaskPipeline
from server.task_pipeline.task_manager import TaskManager
from server.config import Config


class Server:
    def __init__(self):
        self.task_pipeline: Optional[TaskPipeline] = None

    def initialize(self) -> None:
        """Initialize all server components."""
        try:
            print("Initializing server components...")

            self.task_pipeline = TaskPipeline(num_workers=4)
            TaskManager.initialize(self.task_pipeline)

            Config.initialize(
                price_per_unit=0.20,  # £0.20 per kWh
                standing_charge=0.25  # £0.25 per day
            )

            print("Server initialization completed successfully")

        except Exception as e:
            print(f"Error during server initialization: {str(e)}")
            raise


def main() -> None:
    """Main entry point for the server application."""
    server = Server()

    try:
        server.initialize()
        print("\nServer is running.")
        while True:
            pass

    except Exception as e:
        print(f"Critical error in server main: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
