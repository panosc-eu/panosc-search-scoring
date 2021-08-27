from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# compute status model
class ComputeStatusModel(BaseModel):
  requested: datetime
  started: Optional[datetime]
  ended: Optional[datetime]
  inProgress: bool

  