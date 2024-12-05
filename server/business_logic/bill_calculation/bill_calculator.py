from datetime import datetime
from typing import Optional
from models.bill_data import BillData
from models.meter_reading import MeterReading
from server.business_logic.bill_calculation.bill_data_validator import BillDataValidator


class BillCalculator:
    def __init__(self, price_per_unit: float, standing_charge: float):
        self.price_per_unit = price_per_unit
        self.standing_charge = standing_charge
        # Validate prices
        BillDataValidator.validate_prices(self.price_per_unit, self.standing_charge)

    def calculate_bill(
        self,
        current_reading: MeterReading,
        previous_reading: Optional[MeterReading],
    ) -> BillData:

        # Validate current reading
        BillDataValidator.validate_reading(current_reading.reading_value)
        BillDataValidator.validate_timestamp(current_reading.timestamp)

        is_initial_reading = previous_reading is None

        # if not is_initial_reading:
        # Validate previous reading
        BillDataValidator.validate_reading(previous_reading.reading_value)
        BillDataValidator.validate_timestamp(previous_reading.timestamp)

        # Validate readings sequence using the validator's method for MeterReading objects
        BillDataValidator.validate_readings_sequence(current_reading, previous_reading)

        # Calculate consumption
        consumption = current_reading.reading_value

        # Calculate billing period in days
        billing_period_timedelta = current_reading.timestamp - previous_reading.timestamp
        billing_period = billing_period_timedelta.total_seconds() / (24 * 3600)

        # Calculate costs
        consumption_cost = consumption * self.price_per_unit
        total_standing_charge = self.standing_charge * billing_period
        total_bill = consumption_cost + total_standing_charge

        billing_period_start = previous_reading.timestamp
        billing_period_end = current_reading.timestamp
        """ else:
            # Initial reading scenario
            consumption = 0.0
            billing_period = 0.0
            consumption_cost = 0.0
            total_standing_charge = 0.0
            total_bill = 0.0
            billing_period_start = current_reading.timestamp
            billing_period_end = current_reading.timestamp"""

        # Create and return BillData
        bill_data = BillData(
            meter_id=current_reading.meter_id,
            consumption=consumption,
            billing_period=billing_period,
            billing_period_start=billing_period_start,
            billing_period_end=billing_period_end,
            consumption_cost=consumption_cost,
            total_standing_charge=total_standing_charge,
            total_bill=total_bill,
            timestamp=datetime.now(),
            is_initial_reading=is_initial_reading,
        )

        return bill_data
