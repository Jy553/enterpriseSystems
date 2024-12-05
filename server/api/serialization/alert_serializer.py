import json
from models.alert import Alert


class AlertSerializer:
    @staticmethod
    def alert_to_json(alert: Alert) -> str:
        """Convert an Alert object to a JSON string."""
        return json.dumps({
            "meterId": alert.meter_id,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat(),
            "alertType": alert.alert_type,
            "readingId": alert.reading_id,
            "severity": alert.severity,
            "resolved": alert.resolved
        }, indent=2)
