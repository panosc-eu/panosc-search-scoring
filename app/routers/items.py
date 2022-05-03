#
# this file contains all the code implementing the documents endpoint of FPS
#

# importing libraries
from fastapi import APIRouter, Request, Response, status, Body, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
import json

#from starlette import responses
#from asgiref.sync import sync_to_async

from ..models.items import \
  ItemModel, \
  ItemPutModel, \
  ItemPutModel, \
  ItemPatchModel, \
  ItemCreationResponseModel, \
  ItemsCountResponseModel, \
  ItemPutResponseModel, \
  ItemPatchResponseModel, \
  ItemDeleteResponseModel
from ..common.utils import debug

# main tag, route and database collection for items
endpointRoute = 'items'
LIMIT_DEFAULT = 1000

# instantiate the fastapi router object
router = APIRouter(
  prefix='/' + endpointRoute,
  tags=[endpointRoute]
)

# Route GET:/items
@router.get(
  "/",
  response_model=List[ItemModel],
  status_code=200,
  response_model_by_alias=False
)
async def get_items(req: Request, limit: int = LIMIT_DEFAULT, offset: int = 0):
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
      '$limit' : limit if limit > 0 else LIMIT_DEFAULT
    }
  )
  # retrieve results
  #items = await db[endpointRoute].find().skip(offset).to_list(limit)
  items = await db[endpointRoute].aggregate(pipeline).to_list(length=None)

  return jsonable_encoder(items,by_alias=False)


# Route GET:/items/count
@router.get(
  "/count", 
  response_model=ItemsCountResponseModel,
  status_code=200
)
async def count_items(req: Request):
  # extract db and config from the app class
  config = req.app.state.config
  db = req.app.state.db_database
  
  # retrieve results
  debug(config,endpointRoute)
  count = await db[endpointRoute].count_documents({})
  return {
    "count": count
  }


# Route GET:/items/<id>
@router.get(
  "/{item_id:path}",
  response_model=ItemModel,
  status_code=200,
  response_model_by_alias=False,
  responses={
    404: {
      'Model': None
    }
  }
)
async def get_item(
    req: Request
):
  # extract db and config from the app class
  config = req.app.state.config
  db = req.app.state.db_database
  
  item_id = req.path_params['item_id']

  debug(config,"get item : " + item_id)
  # retrieve results
  item = await db[endpointRoute].find_one({'_id':item_id})
  if not item:
    # item not found
    return JSONResponse(
      status_code=404,
      content=None
    )

  # fix id issue
  item['id'] = item['_id']
  del item['_id']
  
  return item


# Route POST:/items
@router.post(
  "/", 
  response_model=ItemCreationResponseModel,
  status_code=201
)
async def new_items(req: Request, inputItems = Body(...)): #List[ItemCreateModel]):
  # extract db and config from the app class
  config = req.app.state.config
  db = req.app.state.db_database
  
  debug(config,inputItems)
  
  try: 
    # check if we get a string in input. 
    # If that's the case, it will try to convert it to a python data type
    if type(inputItems) is str:
      debug(config,"Converting input to python type")
      inputItems = json.loads(inputItems)

    # check if we need to insert one or many
    writtenItems = 0
    if type(inputItems) is dict:
      # we have only one item to insert
      modeledItem = jsonable_encoder(ItemModel(**inputItems), by_alias=True)
      results = await db[endpointRoute].insert_one(modeledItem)
      itemsId = [results.inserted_id] if (type(results.inserted_id) is str and results.inserted_id) else []
    elif type(inputItems) is list:
      # we assume that we have many items to insert
      modeledItems = jsonable_encoder([ItemModel(**item) for item in inputItems], by_alias=True)
      results = await db[endpointRoute].insert_many(modeledItems)
      itemsId = results.inserted_ids
    else:
      raise HTTPException(status_code=422,detail="Invalid data")

    return {
      'success' : True,
      'items_created' : len(itemsId),
      'items_ids' : itemsId
    }
    
  except Exception as e:
    raise HTTPException(
      status_code=400,
      detail="An exception of type {0} occurred. Arguments:\n{1!r}".format(type(e).__name__, e.args)
    )



# Route DELETE:/items/<id>
@router.delete(
  "/{item_id:path}",
  response_model=ItemDeleteResponseModel,
  status_code=200
)
async def delete_item(
    req: Request
):
  # extract db and config from the app class
  config = req.app.state.config
  db = req.app.state.db_database

  item_id = req.path_params['item_id']

  debug(config,'Delete : ' + item_id)
  # delete results
  res = await db[endpointRoute].delete_many({'_id':item_id})
  # fix id issue
  return {
    'successful' : True if res.deleted_count == 1 else False,
    'items_deleted' : res.deleted_count
  }


# Route PUT:/items/<id>
# replace 
@router.put(
  "/{item_id}",
  response_model=ItemPutResponseModel,
  status_code=200
)
async def update_whole_item(
    req: Request, 
    item_id:str, 
    item:ItemPutModel
):
  # extract db and config from the app class
  config = req.app.state.config
  db = req.app.state.db_database

  # prepare item
  prep_item = jsonable_encoder(item,exclude_unset=True)
  # update item
  res = await db[endpointRoute].replace_one(
    {'_id': item_id},
    prep_item
  )

  return {
    'successful' : True if res.modified_count == 1 else False,
    'items_updated' : res.modified_count
  }



# Route PATCH:/items/<id>
@router.patch(
  "/{item_id}",
  response_model=ItemPatchResponseModel,
  status_code=200
)
async def update_partial_item(
    req: Request, 
    item_id:str, 
    item:ItemPatchModel
):
  # extract db and config from the app class
  config = req.app.state.config
  db = req.app.state.db_database

  # prepare item
  prep_item = jsonable_encoder(item,exclude_unset=True)
  # update item
  res = await db[endpointRoute].update_one(
    {'_id': item_id},
    {'$set' : prep_item}
  )

  return {
    'successful' : True if res.modified_count == 1 else False,
    'items_updated' : res.modified_count
  }
  
