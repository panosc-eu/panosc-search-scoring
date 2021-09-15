from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

# weight element
class WeightModel(BaseModel):
  id: UUID = Field(alias='_id')
  term: str
  itemId: UUID
  timestamp: datetime
  value: float

  class Config:
    allow_population_by_field_name = True


class WeightResponseModel(WeightModel):
  itemGroup: Optional[str] = "default"


# items count model
class WeightsCountResponseModel(BaseModel):
  count: int

