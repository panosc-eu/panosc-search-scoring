from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from uuid import UUID, uuid4

# item model
class ItemModel(BaseModel):
  #id: UUID = Field(default_factory=uuid4,alias='_id')
  #id: UUID = Field(alias='_id')
  id: str = Field(alias='_id')
  group: str = "default"
  fields: Dict = {}
  terms: List = []

  class Config:
    allow_population_by_field_name = True


# create item model
# not needed anymore
#class ItemCreateModel(BaseModel):
#  id: Optional[UUID] = Field(default_factory=uuid4,alias='_id')
#  group: Optional[str] = "default"
#  fields: Dict = {}
#
#  class Config:
#    allow_population_by_field_name = True

# update item model
class ItemPutModel(BaseModel):
  group: str
  fields: Dict

class ItemPatchModel(BaseModel):
  group: Optional[str] = None
  fields: Optional[Dict] = None


# item creation model
class ItemCreationResponseModel(BaseModel):
  success: bool
  items_created: int
  items_ids: List[str]
  logs: List[str]

# items count model
class ItemsCountResponseModel(BaseModel):
  count: int

# items put/replace model
class ItemPutResponseModel(BaseModel):
  successful: bool
  items_updated: int

# items patch/update model
class ItemPatchResponseModel(ItemPutResponseModel):
  pass

# items put/replace model
class ItemDeleteResponseModel(BaseModel):
  successful: bool
  items_deleted: int
