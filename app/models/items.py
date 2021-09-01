from pydantic import BaseModel, Field
from typing import Dict, Optional
from uuid import UUID, uuid4

# item model
class ItemModel(BaseModel):
  id: UUID = Field(default_factory=uuid4,alias='_id')
  group: str = "default"
  fields: Dict = {}

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
class ItemUpdateModel(BaseModel):
  group: Optional[str]
  fields: Optional[Dict]
  
