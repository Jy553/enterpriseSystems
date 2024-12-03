import datetime
from dataclasses import dataclass


@dataclass
class BillData:
    meter_id: str
    consumption: float
    billing_period: float
    billing_period_start: datetime.datetime
    billing_period_end: datetime.datetime
    consumption_cost: float
    total_standing_charge: float
    total_bill: float
    timestamp: datetime.datetime
    is_initial_reading: bool
