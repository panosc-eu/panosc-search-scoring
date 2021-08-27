#
# this file contains all the code implementing the documents endpoint of FPS
#

# importing libraries
from fastapi import APIRouter, Request, Body
from typing import List

from ..models.items import ItemModel, ItemCreateModel

# main tag for items
itemsRoute = 'items'

# instantiate the fastapi router object
router = APIRouter(
  prefix='/' + itemsRoute,
  tags=[itemsRoute]
)

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
async def new_items(req: Request, inputItems = Body(...)): #List[ItemCreateModel]):
  # extract db and config from the app class
  config = req.app.app_config
  db = req.app.app_db
  
  # check if we need to insert one or many
  if type(inputItems) is dict:
    # we have only one item to insert
    modeledItem = ItemModel(**inputItems)
    results = await db[itemsRoute].insert_one(modeledItem)
  elif type(inputItems) is list:
    # we assume that we have many items to insert
    modeledItems = [ItemModel(**item) for item in inputItems]
    results = await db[itemsRoute].insert_many(modeledItems)
  else:
    raise Exception("Invalid data")

  return {
    'result' : 'success',
    'items-created' : 1
  }

# Route PUT:/items/<id>
@router.put("/{item_id}")
async def update_whole_item(item_id:str, item: ItemModel):
  return "Update whole item"

# Route PATCH:/items/<id>
@router.patch("/{item_id}")
async def update_partial_item(item_id:str, item:ItemModel):
  return "Update partial item"
  # example code
  # stored_item_data = get data from db
  store_item_model = Item(**stored_item_data)
  update_data = item.dict(exclude_unset=True)
  updated_item = stored_item_model.copy(update=update_data)
  # save item in db

