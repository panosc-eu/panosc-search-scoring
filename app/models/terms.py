from pydantic import BaseModel
from typing import List

# endpoint output
class TermListModel(BaseModel):
  group: str = 'all'
  terms: List[str]
