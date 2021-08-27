from pydantic import BaseModel
from typing import Optional, List

# score request model. Body of the post request
class ScoreRequestModel(BaseModel):
  query: str
  itemIds: Optional[List[str]] = []
  groups: Optional[List[str]] = ["all"]
  grouped: Optional[bool] = False
  limit: Optional[int] = 50

# scored item model
class ScoredItemModel(BaseModel):
  id: str
  score: float = 0.0
  group: Optional[str] = "none"

class GroupedItemsModel(BaseModel):
  group: str = 'default'
  items: List[ScoredItemModel]

# query informartion model
class ScoreQueryModel(BaseModel):
  query: str
  terms: List[str]

class ScoresOutputModel(BaseModel):
  query: ScoreQueryModel
  scores: List[ScoredItemModel]
  grouped: Optional[List[GroupedItemsModel]]
  length: int
