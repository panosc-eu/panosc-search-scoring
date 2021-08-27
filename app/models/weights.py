from pydantic import BaseModel
from datetime import datetime

# weight element
class WeightModel(BaseModel):
  term: str
  itemId: str
  timestamp: datetime
  value: float