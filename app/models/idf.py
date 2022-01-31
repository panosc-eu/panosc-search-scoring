from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

# weight element
class IdfModel(BaseModel):
  id: Optional[UUID] = Field(default_factory=uuid4,alias='_id')
  term: str
  group: Optional[str] = "default"
  timestamp: datetime
  IDF: float

  class Config:
    allow_population_by_field_name = True


class IdfResponseModel(BaseModel):
  term: str
  group: str
  timestamp: datetime
  IDF: float


# items count model
class IdfCountResponseModel(BaseModel):
  count: int

