from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Alert:
    meter_id: str
    message: str
    timestamp: datetime
    alert_type: str  # e.g., "VALIDATION_ERROR", "METER_CHECK_REQUIRED"
    reading_id: Optional[str] = None
    severity: str = "HIGH"  # Default to HIGH for validation errors
    resolved: bool = False
