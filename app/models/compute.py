from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4


# compute status model
class ComputeStatusModel(BaseModel):
  id: UUID = Field(default_factory=uuid4,alias='_id')
  requested: datetime
  started: Optional[datetime] = None
  ended: Optional[datetime] = None
  progressPercent: Optional[float] = 0
  progressDescription: Optional[str] = ""
  inProgress: bool


class ComputeStatusResponseModel(BaseModel):
  requested: Optional[datetime] = None
  started: Optional[datetime] = None
  ended: Optional[datetime] = None
  progressPercent: Optional[float] = 0
  progressDescription: Optional[str] = ""
  inProgress: bool
  