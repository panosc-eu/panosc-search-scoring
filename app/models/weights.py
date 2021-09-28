from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

# weight element
class WeightModel(BaseModel):
  id: Optional[UUID] = Field(default_factory=uuid4,alias='_id')
  term: str
  itemId: str
  itemGroup: Optional[str] = "default"
  timestamp: datetime
  value: float

  class Config:
    allow_population_by_field_name = True


class WeightResponseModel(WeightModel):
  pass


# items count model
class WeightsCountResponseModel(BaseModel):
  count: int

