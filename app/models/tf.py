from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

# weight element
class TfModel(BaseModel):
  id: Optional[UUID] = Field(default_factory=uuid4,alias='_id')
  term: str
  itemId: str
  group: Optional[str] = "default"
  timestamp: datetime
  TF: float

  class Config:
    allow_population_by_field_name = True


class TfResponseModel(BaseModel):
  term: str
  itemId: str
  group: str
  timestamp: datetime
  TF: float


# items count model
class TfCountResponseModel(BaseModel):
  count: int

