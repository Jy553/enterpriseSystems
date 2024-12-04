import unittest
from unittest.mock import patch, MagicMock
from smart_meter_client import SmartMeterApp
import customtkinter as ctk

class test_smart_meter_app(unittest.TestCase):

    def setUp(self):
        """Set up the application instance before each test."""
        self.app = SmartMeterApp()

    def tearDown(self):
        """Clean up after each test."""
        self.app.destroy()

    @patch("smart_meter_app.psutil.net_if_addrs")
    def test_get_unique_device_id(self, mock_net_if_addrs):
        """Test MAC address retrieval as unique device ID."""
        mock_net_if_addrs.return_value = {
            "eth0": [MagicMock(family=psutil.AF_LINK, address="00:1A:2B:3C:4D:5E")]
        }
        device_id = self.app.get_unique_device_id()
        self.assertEqual(device_id, "00:1A:2B:3C:4D:5E")

    def test_initial_ui_setup(self):
        """Test that UI components are initialized correctly."""
        self.assertEqual(self.app.title(), "SmartMeter")
        self.assertEqual(self.app.geometry(), "500x400")
        self.assertEqual(self.app.current_bill, 0)
        self.assertEqual(self.app.total_usage, 0)

    def test_mode_toggle(self):
        """Test toggling between dark and light mode."""
        initial_mode = ctk.get_appearance_mode()
        self.app.toggle_mode()
        self.assertNotEqual(ctk.get_appearance_mode(), initial_mode)

    @patch("smart_meter_client.simulate_server_communication")
    def test_update_bill(self, mock_simulate_server_communication):
        """Test that bill and usage update correctly."""
        mock_simulate_server_communication.return_value = (2.5, 1.2)
        self.app.current_bill = 0
        self.app.total_usage = 0

        # Simulate an update
        self.app.update_bill()

        # Verify increments
        self.assertEqual(self.app.current_bill, 2.5)
        self.assertEqual(self.app.total_usage, 1.2)

    def test_console_logging(self):
        """Test that logs are correctly written to the console."""
        message = "Test log message"
        self.app.log_to_console(message)
        self.assertIn(message, self.app.console_textbox.get("1.0", "end"))

    @patch("smart_meter_client.ApiHandler")
    def test_network_failure_reconnection(self, mock_ApiHandler):
        """Simulate a network failure and verify reconnection."""
        mock_handler_instance = mock_ApiHandler.return_value.__enter__.return_value
        self.app.update_bill()  # Should log a network failure and attempt reconnection

        # Ensure network failure and reconnection logs appear
        log_text = self.app.console_textbox.get("1.0", "end")
        self.assertIn("Network lost... Trying to reconnect.", log_text)
        self.assertIn("Reconnected to the network.", log_text)

    def test_reset_state(self):
        """Test that resetting clears bill, usage, and console logs."""
        self.app.current_bill = 100
        self.app.total_usage = 50
        self.app.log_to_console("Dummy log")
        
        # Perform reset
        self.app.reset_state()
        
        # Assert reset values
        self.assertEqual(self.app.current_bill, 0)
        self.assertEqual(self.app.total_usage, 0)
        self.assertEqual(self.app.console_textbox.get("1.0", "end").strip(), "")

if __name__ == "__main__":
    unittest.main()
