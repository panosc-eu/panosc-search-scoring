from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

# score request model. Body of the post request
class ScoreRequestModel(BaseModel):
  query: str
  itemIds: Optional[List[str]] = []
  group: Optional[str] = ""
  limit: Optional[int] = -1

# scored item model
class ScoredItemModel(BaseModel):
  id: str
  score: float = 0.0
  group: Optional[str] = ""

class GroupedItemsModel(BaseModel):
  group: str = 'default'
  items: List[ScoredItemModel]

# query informartion model
class ScoreQueryModel(BaseModel):
  query: str
  terms: List[str]

class ScoreResponseModel(BaseModel):
  request: ScoreRequestModel
  query: ScoreQueryModel
  scores: List[ScoredItemModel]
  #grouped: Optional[List[GroupedItemsModel]]
  dimension: int
  computeInProgress: bool
  started: datetime
  ended: datetime

class ScoresResultsModel(BaseModel):
  query: ScoreQueryModel
  scores: List[ScoredItemModel]
