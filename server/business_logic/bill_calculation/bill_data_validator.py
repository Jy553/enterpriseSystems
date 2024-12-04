import datetime
from typing import Optional
from models.meter_reading import MeterReading


class BillDataValidator:
    @staticmethod
    def validate_reading(reading: float) -> None:
        if reading < 0:
            raise ValueError("Meter reading cannot be negative")

    @staticmethod
    def validate_prices(price_per_unit: float, standing_charge: float) -> None:
        if price_per_unit <= 0:
            raise ValueError("Price per unit must be positive")
        if standing_charge < 0:
            raise ValueError("Standing charge cannot be negative")

    @staticmethod
    def validate_timestamp(timestamp: datetime.datetime) -> None:
        if timestamp > datetime.datetime.now():
            raise ValueError("Timestamp cannot be in the future")

    @staticmethod
    def validate_readings_sequence(current: MeterReading, previous: Optional[MeterReading]) -> None:
        if previous is None:
            return

        if current.reading_value < previous.reading_value:
            raise ValueError(
                f"Current reading ({current.reading_value})"
                f"cannot be less than previous reading ({previous.reading_value})"
            )

        if current.timestamp <= previous.timestamp:
            raise ValueError("Current timestamp must be later than previous timestamp")

        timestamp_diff = current.timestamp - previous.timestamp
        billing_period = timestamp_diff.total_seconds() / (24 * 3600)
        if billing_period > 366:
            raise ValueError(f"Billing period ({billing_period} days) exceeds maximum allowed duration")

    @staticmethod
    def validate_billing_period(current_timestamp: datetime.datetime,
                                previous_timestamp: datetime.datetime) -> None:
        timestamp_diff = current_timestamp - previous_timestamp

        if timestamp_diff.total_seconds() < 0:
            raise ValueError("Current timestamp cannot be earlier than previous timestamp")

        billing_period = timestamp_diff.total_seconds() / (24 * 3600)
        if billing_period > 366:
            raise ValueError(f"Billing period ({billing_period} days) exceeds maximum allowed duration")
