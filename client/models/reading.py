from pydantic import BaseModel, ValidationError
from datetime import datetime
from models.message import Message
class Reading(BaseModel):
    meter_id: str
    reading_value: float
    reading_unit: str = 'kwh'




if __name__ == "__main__":
   try:
    reading = Message[Reading](
       messageType='READING',
        data=Reading(
            meter_id='1',
            reading_value=4.3)
        )
   except ValidationError as e:
      print(e)
   
   print(reading.model_dump_json())
    