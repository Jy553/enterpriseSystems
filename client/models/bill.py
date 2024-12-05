from datetime import datetime
from pydantic import BaseModel, ValidationError

class Bill(BaseModel):
    meter_id: str
    consumption: float
    billing_period: float
    billing_period_start: datetime
    billing_period_end: datetime
    consumption_cost: float
    total_standing_charge: float
    total_bill: float
    is_initial_reading: bool


