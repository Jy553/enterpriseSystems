from datetime import datetime
from typing import TypeVar, Generic
from pydantic import BaseModel, ValidationError

# Define a generic type for the nested data class
T = TypeVar('T')

class Message(BaseModel, Generic[T]): 
    messageType: str
    timestamp: datetime = datetime.now()
    data: T
