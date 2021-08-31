#
# this file contains all the code implementing the documents endpoint of FPS
#

# importing libraries
from fastapi import APIRouter, Request, Body
from fastapi.encoders import jsonable_encoder
from typing import List
from asgiref.sync import sync_to_async

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
async def get_items(req: Request, limit: int = 1000, offset: int = 0):
  # extract db and config from the app class
  config = req.app.state.config
  db = req.app.state.db_database
  
  # pipeline
  pipeline = [
    {
      '$project' : {
        '_id' : 0,
        'id' : { '$toString' : "$_id" },
        'group' : 1,
        'fields' : 1 
      }
    }
  ]
  if offset:
    pipeline.append(
      {
        '$skip' : offset
      }
    )
  pipeline.append(
    {
      '$limit' : limit
    }
  )
  # retrieve results
  #items = await db[itemsRoute].find().skip(offset).to_list(limit)
  items = await db[itemsRoute].aggregate(pipeline).to_list(length=None)

  return items


# Route GET:/items/count
@router.get("/count")
async def count_items(req: Request):
  # extract db and config from the app class
  config = req.app.state.config
  db = req.app.state.db_database
  
  # retrieve results
  count = await db[itemsRoute].count_documents({})
  return count


# Route GET:/items/<id>
@router.get("/{item_id}")
async def get_item(req: Request, item_id: str):
  # extract db and config from the app class
  config = req.app.state.config
  db = req.app.state.db_database
  
  # retrieve results
  item = await db[itemsRoute].find_one({'_id':item_id})
  # fix id issue
  item['id'] = item['_id']
  del item['_id']
  return item


# Route POST:/items
@router.post("/")
async def new_items(req: Request, inputItems = Body(...)): #List[ItemCreateModel]):
  # extract db and config from the app class
  config = req.app.state.config
  db = req.app.state.db_database
  
  # check if we need to insert one or many
  writtenItems = 0
  if type(inputItems) is dict:
    # we have only one item to insert
    modeledItem = jsonable_encoder(ItemModel(**inputItems), by_alias=True)
    results = await db[itemsRoute].insert_one(modeledItem)
    itemsId = [results.inserted_id] if (type(results.inserted_id) is str and results.inserted_id) else []
  elif type(inputItems) is list:
    # we assume that we have many items to insert
    modeledItems = jsonable_encoder([ItemModel(**item) for item in inputItems], by_alias=True)
    results = await db[itemsRoute].insert_many(modeledItems)
    itemsId = results.inserted_ids
  else:
    raise Exception("Invalid data")

  return {
    'result' : 'success',
    'items-created' : {
      'length' : len(itemsId),
      'ids' : itemsId
    }
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


