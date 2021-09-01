#
# this file contains all the code implementing the documents endpoint of FPS
#

# importing libraries
from fastapi import APIRouter, Request, Body
from fastapi.encoders import jsonable_encoder
from typing import List
from asgiref.sync import sync_to_async

from ..models.items import ItemModel, ItemUpdateModel

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
    'success' : True,
    'items-created' : {
      'length' : len(itemsId),
      'ids' : itemsId
    }
  }

# Route DELETE:/items/<id>
@router.delete("/{item_id}")
async def delete_item(req: Request, item_id: str):
  # extract db and config from the app class
  config = req.app.state.config
  db = req.app.state.db_database

  # delete results
  res = await db[itemsRoute].delete_many({'_id':item_id})
  # fix id issue
  return {
    'successful' : True if res.deleted_count == 1 else False,
    'items-deleted' : res.deleted_count
  }


# Route PUT:/items/<id>
# replace 
@router.put("/{item_id}")
async def update_whole_item(req: Request, item_id:str, item:ItemUpdateModel):
  # extract db and config from the app class
  config = req.app.state.config
  db = req.app.state.db_database

  # prepare item
  prep_item = jsonable_encoder(item,exclude_unset=True)
  # update item
  res = await db[itemsRoute].replace_one(
    {'_id': item_id},
    prep_item
  )

  return {
    'successful' : True if res.modified_count == 1 else False,
    'items_updated' : res.modified_count
  }



# Route PATCH:/items/<id>
@router.patch("/{item_id}")
async def update_partial_item(req: Request, item_id:str, item:ItemUpdateModel):
  # extract db and config from the app class
  config = req.app.state.config
  db = req.app.state.db_database

  # prepare item
  prep_item = jsonable_encoder(item,exclude_unset=True)
  # update item
  res = await db[itemsRoute].update_one(
    {'_id': item_id},
    {'$set' : prep_item}
  )

  return {
    'successful' : True if res.modified_count == 1 else False,
    'items_updated' : res.modified_count
  }
  
