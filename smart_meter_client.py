import customtkinter as ctk
import random
import time
import uuid
import platform
import re
from threading import Thread
from datetime import datetime
import psutil  # You'll need to install this package with `pip install psutil`


# Simulate server communication to fetch the latest bill and usage
def simulate_server_communication():
    bill_increment = round(random.uniform(1, 5), 2)
    usage_increment = round(random.uniform(0.5, 2), 2)
    return bill_increment, usage_increment


class SmartMeterApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Window title and fixed size
        self.title("SmartMeter")
        self.geometry("500x400")
        self.resizable(False, False)

        # Configure grid
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Cog icon for settings access (top right corner)
        self.cog_button = ctk.CTkButton(self, text="⚙", width=30, command=self.show_settings_page)
        self.cog_button.grid(row=0, column=0, sticky="ne", padx=10, pady=10)

        # Main view
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Main view widgets
        self.title_label = ctk.CTkLabel(self.main_frame, text="Smart Meter Interface", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, pady=(0, 20), sticky="n")

        self.bill_label = ctk.CTkLabel(self.main_frame, text="Current Bill: £0.00", font=ctk.CTkFont(size=18))
        self.bill_label.grid(row=1, column=0, pady=(10, 5), sticky="n")

        self.usage_label = ctk.CTkLabel(self.main_frame, text="Total Usage: 0.00 kWh", font=ctk.CTkFont(size=16))
        self.usage_label.grid(row=2, column=0, pady=(5, 5), sticky="n")

        self.last_updated_label = ctk.CTkLabel(self.main_frame, text="Last Updated: N/A", font=ctk.CTkFont(size=14))
        self.last_updated_label.grid(row=3, column=0, pady=(5, 10), sticky="n")

        self.console_toggle_button = ctk.CTkButton(self.main_frame, text="Show Console", command=self.toggle_console)
        self.console_toggle_button.grid(row=5, column=0, pady=10)

        self.console_frame = ctk.CTkFrame(self.main_frame)
        self.console_frame.grid(row=6, column=0, sticky="nsew", pady=10)
        self.console_textbox = ctk.CTkTextbox(self.console_frame, height=100, state="disabled")
        self.console_textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.console_frame.grid_columnconfigure(0, weight=1)
        self.console_frame.grid_rowconfigure(0, weight=1)
        self.console_frame.grid_remove()

        self.current_bill = 0
        self.total_usage = 0

        # Settings page setup
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.grid_rowconfigure(0, weight=0)
        self.settings_frame.grid_rowconfigure(1, weight=0)
        self.settings_frame.grid_rowconfigure(2, weight=0)
        self.settings_frame.grid_rowconfigure(3, weight=0)
        self.settings_frame.grid_rowconfigure(4, weight=0)
        self.settings_frame.grid_columnconfigure(0, weight=1)

        self.account_label = ctk.CTkLabel(self.settings_frame, text=f"Account Reader ID: {self.get_unique_device_id()}", font=ctk.CTkFont(size=16))
        self.account_label.grid(row=0, column=0, pady=(20, 10), sticky="n")

        self.version_label = ctk.CTkLabel(self.settings_frame, text="Software Version: 1.0.0", font=ctk.CTkFont(size=16))
        self.version_label.grid(row=1, column=0, pady=(10, 10), sticky="n")

        self.mode_toggle_button = ctk.CTkSwitch(self.settings_frame, text="Dark Mode", command=self.toggle_mode, onvalue="dark", offvalue="light")
        self.mode_toggle_button.grid(row=2, column=0, pady=(10, 10), sticky="n")

        self.reset_button = ctk.CTkButton(self.settings_frame, text="Reset", command=self.reset_state)
        self.reset_button.grid(row=3, column=0, pady=20)

        self.back_button = ctk.CTkButton(self.settings_frame, text="Back", command=self.show_main_page)
        self.back_button.grid(row=4, column=0, pady=10)

        self.settings_frame.grid_remove()

        # Start the background thread to update the bill and usage
        self.start_bill_updates()

    def get_unique_device_id(self):
        # Retrieve MAC address as a unique identifier
        try:
            mac = psutil.net_if_addrs()
            for iface_name, iface_list in mac.items():
                for iface in iface_list:
                    if iface.family == psutil.AF_LINK:
                        return iface.address
        except Exception as e:
            return str(uuid.uuid4())  # Fallback to UUID if MAC address retrieval fails

    def toggle_mode(self):
        if self.mode_toggle_button.get() == "dark":
            ctk.set_appearance_mode("dark")
            self.mode_toggle_button.configure(text="Light Mode")
        else:
            ctk.set_appearance_mode("light")
            self.mode_toggle_button.configure(text="Dark Mode")

    def toggle_console(self):
        if self.console_frame.winfo_ismapped():
            self.console_frame.grid_remove()
            self.console_toggle_button.configure(text="Show Console")
            self.geometry("500x400")
        else:
            self.console_frame.grid()
            self.console_toggle_button.configure(text="Hide Console")
            self.geometry("500x455")  # Adjust window size when console is shown

    def start_bill_updates(self):
        thread = Thread(target=self.update_bill)
        thread.daemon = True
        thread.start()

    def update_bill(self):
        try:
            while True:
                # Simulate a 2-second interval between bill updates
                time.sleep(2)

                if random.random() < 0.1:  # 10% chance of network failure
                    self.log_to_console("Network lost... Trying to reconnect.")
                    time.sleep(2)  # Simulate downtime during network loss
                    self.log_to_console("Reconnected to the network.")
                    continue  # Skip updating the bill during a network outage

                # Fetch the latest bill and usage (simulated server response)
                bill_increment, usage_increment = simulate_server_communication()
                self.current_bill += bill_increment
                self.total_usage += usage_increment

                # Update the bill and usage labels
                self.bill_label.configure(text=f"Current Bill: £{self.current_bill:.2f}")
                self.usage_label.configure(text=f"Total Usage: {self.total_usage:.2f} kWh")

                # Update the last updated time
                last_updated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.last_updated_label.configure(text=f"Last Updated: {last_updated_time}")

                # Log the action in the console with a timestamp
                self.log_to_console(f"[{last_updated_time}] Bill updated: £{self.current_bill:.2f}, Usage: {self.total_usage:.2f} kWh")

        except Exception as e:
            # Log error messages to the console instead of showing pop-ups
            self.log_to_console(f"Error occurred: {str(e)}")

    def log_to_console(self, message):
        self.console_textbox.configure(state="normal")
        self.console_textbox.insert(ctk.END, f"{message}\n")
        self.console_textbox.see(ctk.END)
        self.console_textbox.configure(state="disabled")

    # Show the settings page
    def show_settings_page(self):
        self.main_frame.grid_remove()
        self.settings_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

    # Show the main page
    def show_main_page(self):
        self.settings_frame.grid_remove()
        self.main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

    # Reset the application state (bill, usage, and console)
    def reset_state(self):
        self.current_bill = 0
        self.total_usage = 0
        self.bill_label.configure(text="Current Bill: £0.00")
        self.usage_label.configure(text="Total Usage: 0.00 kWh")
        self.last_updated_label.configure(text="Last Updated: N/A")
        self.console_textbox.configure(state="normal")
        self.console_textbox.delete(1.0, ctk.END)
        self.console_textbox.configure(state="disabled")


if __name__ == "__main__":
    app = SmartMeterApp()
    app.mainloop()
