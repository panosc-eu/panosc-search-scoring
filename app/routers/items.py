#
# this file contains all the code implementing the documents endpoint of FPS
#

# importing libraries
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List

# instantiate the fastapi router object
router = APIRouter(
  prefix='/items',
  tags=['items']
)

# item model
class Item(BaseModel):
  id: str
  group: str = "default"
  fields: Dict = {}


# Route GET:/items
@router.get("/")
async def get_items():
  return "Get all items"

# Route GET:/items/<id>
@router.get("/{item_id}")
async def get_item(item_id: str):
  return "Get item with id {}".format(item_id)

# Route POST:/items
@router.post("/")
async def new_items(items: List[Item]):
  return "Created items"

# Route PUT:/items/<id>
@router.put("/{item_id}")
async def update_whole_item(item_id:str, item: Item):
  return "Update whole item"

# Route PATCH:/items/<id>
@router.patch("/{item_id}")
async def update_partial_item(item_id:str, item:Item):
  return "Update partial item"
  # example code
  # stored_item_data = get data from db
  store_item_model = Item(**stored_item_data)
  update_data = item.dict(exclude_unset=True)
  updated_item = stored_item_model.copy(update=update_data)
  # save item in db

