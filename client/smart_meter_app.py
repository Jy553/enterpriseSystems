import hashlib
from tkinter import messagebox
import customtkinter as ctk
import random
import time
from datetime import datetime
import threading
import logging
import psutil
import uuid
from messaging_client import MessagingClient
from models.bill import Bill
from models.reading import Reading
from models.message import Message
# Configure logging to help us track the application's behavior
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartMeterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Initialize messaging client for RabbitMQ communication
        self.messaging_client = MessagingClient()
        self.readings_thread = None
        self.connected = threading.Event()

        self._meter_reading = 0.0
        self.current_bill = 0.0
        self.uuid = None

        # Set up the UI
        self._setup_ui()

        # Start connection to messaging service
        self.start_connection()

    def create_reading(self):
        """Creates a new reading representing current meter state."""
        current_time = datetime.now()

        # Create the reading message
        reading = Message[Reading](
            messageType='READING',
            timestamp=current_time,
            data=Reading(
                meter_id=str(self.get_unique_device_id()),
                reading_value=self.total_usage,  # This is correct - it's the current meter state
                reading_unit='kwh'
            )
        )

        # Log the actual reading being sent
        print(f"Sending meter reading - Total consumption: {self.total_usage:.2f} kWh")

        return reading

    def _setup_ui(self):
        """Set up the user interface components."""
        # Window configuration
        self.title("SmartMeter")
        self.geometry("500x400")
        self.resizable(False, False)

        # Grid configuration
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create and configure UI components
        self._setup_main_frame()
        self._setup_settings_frame()

        # Initially hide settings frame
        self.settings_frame.grid_remove()

    def _setup_main_frame(self):
        """Set up the main application frame and its components."""
        # Settings button (cog icon)
        self.cog_button = ctk.CTkButton(self, text="⚙", width=30, command=self.show_settings_page)
        self.cog_button.grid(row=0, column=0, sticky="ne", padx=10, pady=10)

        # Connection retry button
        self.connection_button = ctk.CTkButton(self, text="Retry Connection", width=30, command=self.start_connection)

        # Main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Smart Meter Interface",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, pady=(0, 20), sticky="n")

        # Bill display
        self.bill_label = ctk.CTkLabel(
            self.main_frame,
            text="Current Bill: £0.00",
            font=ctk.CTkFont(size=18)
        )
        self.bill_label.grid(row=1, column=0, pady=(10, 5), sticky="n")

        # Usage display
        self.usage_label = ctk.CTkLabel(
            self.main_frame,
            text="Total Usage: 0.00 kWh",
            font=ctk.CTkFont(size=16)
        )
        self.usage_label.grid(row=2, column=0, pady=(5, 5), sticky="n")

        # Last updated timestamp
        self.last_updated_label = ctk.CTkLabel(
            self.main_frame,
            text="Last Updated: Connecting",
            font=ctk.CTkFont(size=14)
        )
        self.last_updated_label.grid(row=3, column=0, pady=(5, 10), sticky="n")

        # Console toggle button
        self.console_toggle_button = ctk.CTkButton(
            self.main_frame,
            text="Show Console",
            command=self.toggle_console
        )
        self.console_toggle_button.grid(row=5, column=0, pady=10)

        # Console frame
        self.console_frame = ctk.CTkFrame(self.main_frame)
        self.console_frame.grid(row=6, column=0, sticky="nsew", pady=10)
        self.console_textbox = ctk.CTkTextbox(self.console_frame, height=100, state="disabled")
        self.console_textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.console_frame.grid_columnconfigure(0, weight=1)
        self.console_frame.grid_rowconfigure(0, weight=1)
        self.console_frame.grid_remove()

    def _setup_settings_frame(self):
        """Set up the settings page frame and its components."""
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.grid_rowconfigure((0, 1, 2, 3, 4), weight=0)
        self.settings_frame.grid_columnconfigure(0, weight=1)

        # Account ID display
        self.account_label = ctk.CTkLabel(
            self.settings_frame,
            text=f"Account Reader ID: {self.get_unique_device_id()}",
            font=ctk.CTkFont(size=16)
        )
        self.account_label.grid(row=0, column=0, pady=(20, 10), sticky="n")

        # Version display
        self.version_label = ctk.CTkLabel(
            self.settings_frame,
            text="Software Version: 1.0.0",
            font=ctk.CTkFont(size=16)
        )
        self.version_label.grid(row=1, column=0, pady=(10, 10), sticky="n")

        # Dark mode toggle
        self.mode_toggle_button = ctk.CTkSwitch(
            self.settings_frame,
            text="Dark Mode",
            command=self.toggle_mode,
            onvalue="dark",
            offvalue="light"
        )
        self.mode_toggle_button.grid(row=2, column=0, pady=(10, 10), sticky="n")

        # Reset button
        self.reset_button = ctk.CTkButton(
            self.settings_frame,
            text="Reset",
            command=self.reset_state
        )
        self.reset_button.grid(row=3, column=0, pady=20)

        # Back button
        self.back_button = ctk.CTkButton(
            self.settings_frame,
            text="Back",
            command=self.show_main_page
        )
        self.back_button.grid(row=4, column=0, pady=10)

    def get_unique_device_id(self):
        """Generate or retrieve a unique identifier for this meter."""
        if self.uuid is not None:
            return self.uuid

        try:
            mac = psutil.net_if_addrs()
            for iface_name, iface_list in mac.items():
                for iface in iface_list:
                    if iface.family == psutil.AF_LINK:
                        # Create a unique ID based on MAC address and a random number
                        self.uuid = hashlib.sha256(
                            f"{iface.address}{random.randint(1000, 9999)}".encode('utf-8')
                        ).hexdigest()[:16]
                        return self.uuid
        except Exception as e:
            logger.error(f'Failed to retrieve MAC Address: {e}')
            self.uuid = str(uuid.uuid4())
            return self.uuid

    def toggle_mode(self):
        """Toggle between light and dark mode."""
        if self.mode_toggle_button.get() == "dark":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    def toggle_console(self):
        """Toggle the visibility of the console window."""
        if self.console_frame.winfo_ismapped():
            self.console_frame.grid_remove()
            self.console_toggle_button.configure(text="Show Console")
            self.geometry("500x400")
        else:
            self.console_frame.grid()
            self.console_toggle_button.configure(text="Hide Console")
            self.geometry("500x455")

    def start_connection(self):
        """Initialize connection to messaging service."""
        if not self.connected.is_set():
            self.connection_button.grid_forget()
            connection_thread = threading.Thread(target=self._establish_connection)
            connection_thread.daemon = True
            connection_thread.start()

    def _establish_connection(self):
        """Establish connection to the messaging service with retries."""
        retries = 0
        max_retries = 3

        while retries < max_retries and not self.connected.is_set():
            self.last_updated_label.configure(text="Last Updated: Connecting")

            try:
                if self.messaging_client.connect():
                    self.connected.set()
                    self.start_background_services()
                    break

            except Exception as e:
                logger.error(f"Connection attempt {retries + 1} failed: {e}")
                self.log_to_console(f'Failed to connect to service - attempt {retries + 1}')

            retries += 1
            time.sleep(2)  # Wait between retries

        if not self.connected.is_set():
            self.connection_button.grid(row=0, column=0, sticky="ne", padx=60, pady=10)
            self.last_updated_label.configure(text="Last Updated: Offline")
            self.show_popup_message('Failed to establish connection to service.')

    def start_background_services(self):
        """Start the background services for sending readings."""
        if self.connected.is_set():
            self.readings_thread = threading.Thread(target=self._send_readings)
            self.readings_thread.daemon = True
            self.readings_thread.start()
            self.last_updated_label.configure(text="Last Updated: Connected")

    def _send_readings(self):
        """Background thread for sending meter readings."""
        while self.connected.is_set():
            try:
                calculated_value = (self._meter_reading + random.uniform(1.50, 5.0))
                print(f'Meter current value: {self._meter_reading}\n')
                print(f'Meter new reading: {calculated_value}')
                # Create reading message with current accumulated reading
                reading = Message[Reading](
                    messageType='READING',
                    timestamp=datetime.now(),
                    data=Reading(
                        meter_id=str(self.get_unique_device_id()),
                        reading_value=calculated_value,
                        reading_unit='kwh'
                    )
                )

                def handle_response(response):
                    try:
                        print(f"Received response: {response}")
                        bill_data = Message[Bill].model_validate_json(response)

                        # Update from server response
                        self.current_bill = bill_data.data.total_bill
                        # IMPORTANT: We're receiving cumulative readings, not incremental ones
                        self._meter_reading = bill_data.data.consumption

                        self.log_to_console(
                            f"Bill updated: £{self.current_bill:.2f}, "
                            f"Consumption: {self._meter_reading:.2f} kWh"
                        )

                        self.refresh_ui()

                    except Exception as e:
                        self.log_to_console(f"Error processing bill: {e}")
                        print(f"Detailed error: {e}")

                success = self.messaging_client.send_message(
                    'readings',
                    reading.model_dump_json(),
                    handle_response
                )

                if success:
                    self.log_to_console(
                        f"Sent meter reading: {self._meter_reading:.2f} kWh"
                    )

                # Wait random interval (15-60 seconds)
                wait_time = random.uniform(15, 60)
                time.sleep(wait_time)

            except Exception as e:
                self.log_to_console(f"Error sending reading: {e}")
                time.sleep(5)

    def refresh_ui(self):
        """Update the UI with latest values."""
        # Format currency with 2 decimal places
        self.bill_label.configure(text=f"Current Bill: £{self.current_bill:.2f}")
        # Format energy usage with 2 decimal places - using _meter_reading
        self.usage_label.configure(text=f"Total Usage: {self._meter_reading:.2f} kWh")

        # Update timestamp
        last_updated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_updated_label.configure(text=f"Last Updated: {last_updated_time}")

        # Log using correct variable
        self.log_to_console(
            f"[{last_updated_time}] Bill updated: £{self.current_bill:.2f}, "
            f"Usage: {self._meter_reading:.2f} kWh"
        )

    def log_to_console(self, message: str):
        """Log a message to the console window with timestamp."""
        self.console_textbox.configure(state="normal")
        self.console_textbox.insert(ctk.END, f"{message}\n")
        self.console_textbox.see(ctk.END)
        self.console_textbox.configure(state="disabled")

    def show_popup_message(self, message: str):
        """Display a popup message to the user."""
        messagebox.showinfo("Notice", message)

    def show_settings_page(self):
        """Switch to the settings page view."""
        self.main_frame.grid_remove()
        self.settings_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

    def show_main_page(self):
        """Switch to the main page view."""
        self.settings_frame.grid_remove()
        self.main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

    def reset_state(self):
        """Reset the application state."""
        self._meter_reading = 0.0
        self.current_bill = 0.0
        self.bill_label.configure(text="Current Bill: £0.00")
        self.usage_label.configure(text="Total Usage: 0.00 kWh")
        self.last_updated_label.configure(text="Last Updated: N/A")
        self.console_textbox.configure(state="normal")
        self.console_textbox.delete(1.0, ctk.END)
        self.console_textbox.configure(state="disabled")

        def __del__(self):
            """Ensure clean shutdown of messaging client."""
            if self.messaging_client:
                self.messaging_client.close()
                logger.info("Messaging client closed")

if __name__ == "__main__":
    app = SmartMeterApp()
    app.mainloop()