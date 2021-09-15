from pydantic import BaseModel
from typing import List

# endpoint output
class TermResponseModel(BaseModel):
  term: str
  numberOfItems: int
  numberOfGroups: int


# terms count model
class TermsCountResponseModel(BaseModel):
  count: int

