import json
from models.bill_data import BillData


class BillSerializer:
    @staticmethod
    def bill_to_json(bill_data: BillData) -> json:
        return json.dumps({
            'meter_id': bill_data.meter_id,
            'consumption': round(bill_data.consumption, 2),
            'billing_period': round(bill_data.billing_period, 2),
            'billing_period_start': bill_data.billing_period_start.isoformat(),
            'billing_period_end': bill_data.billing_period_end.isoformat(),
            'consumption_cost': round(bill_data.consumption_cost, 2),
            'total_standing_charge': round(bill_data.total_standing_charge, 2),
            'total_bill': round(bill_data.total_bill, 2),
            'timestamp': bill_data.timestamp.isoformat(),
            'is_initial_reading': bill_data.is_initial_reading
        }, indent=2)
