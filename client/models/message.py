from datetime import datetime
from typing import TypeVar, Generic
from pydantic import BaseModel, ConfigDict
T = TypeVar('T')


class Message(BaseModel, Generic[T]):
    messageType: str
    timestamp: datetime
    data: T

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )

    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now()
        super().__init__(**data)