#
# this file contains all the code implementing the terms endpoint of FPS
#

# importing libraries
from fastapi import APIRouter, Request
from typing import List, Optional

from fastapi.encoders import jsonable_encoder


from ..models.terms import TermResponseModel, TermsCountResponseModel
from .items import endpointRoute as itemCollection
from ..common.utils import debug

# terms endpoint 
endpointRoute = "terms"
# terms do not have a collection in the database
# they are stored in the weights collection
databaseCollection = "weights"


# instantiate the fastapi router object
router = APIRouter(
  prefix='/' + endpointRoute,
  tags=[endpointRoute]
)
  
def _getAggregationPipeline(
    itemCollection, 
    group=None,
    count=False 
):
  pipeline = [
    {
      '$lookup' : {
        'from' : itemCollection,
        'localField' : 'itemId',
        'foreignField' : '_id',
        'as' : 'item'
      }
    },
    {
      '$unwind' : '$item'
    },
    {
      '$project' : {
        '_id' :  0,
        'term' : '$term',
        'itemId' : '$itemId',
        'itemGroup' : '$item.group'
      }
    }
  ]

  if group is not None:
    # user has provided the group we need to return
    pipeline.append(
      {
        '$match' : {
          'itemGroup' : group
        }
      }
    )

  # count items and group
  pipeline.append(
    {
      '$group' : {
        '_id' : "$term",
        'numberOfItems' : { '$addToSet' : '$itemId' },
        'numberOfGroups' : { '$addToSet' : '$itemGroup' }
      } 
    }
  )
  pipeline.append(
    {
      '$project' : {
        '_id' : 0,
        'term' : '$_id',
        'numberOfItems' : { '$size' : '$numberOfItems' },
        'numberOfGroups' : { '$size' : '$numberOfGroups' }
      }
    }
  )

  if count:
    pipeline.append(
      {
        '$count' : 'count'
      }
    )

  return pipeline
 

# Route GET:/terms
@router.get(
  "",
  status_code=200,
  response_model=List[TermResponseModel]
)
async def get_terms(
    req: Request,
    group: Optional[str] = None
):
  """
  return all the terms
  If groups is specified, anly the terms in the group are returned
  """
  # extract db and config from the app class
  config = req.app.state.config
  db = req.app.state.db_database

  # build aggregation pipeline
  pipeline = _getAggregationPipeline(
    itemCollection,
    group)

  terms = await db[databaseCollection].aggregate(pipeline).to_list(length=None)
  debug(config,terms)
  return jsonable_encoder(terms, by_alias=False)

    
# Route GET:/weights/count
@router.get(
  "/count", 
  response_model=TermsCountResponseModel,
  status_code=200
)
async def count_weights(
  req: Request,
  group: Optional[str] = None
):
  # extract db and config from the app class
  config = req.app.state.config
  db = req.app.state.db_database
  

  # build aggregation pipeline
  pipeline = _getAggregationPipeline(
    itemCollection,
    group,
    True
  )
  debug(config,pipeline)

  # retrieve results
  count = await db[databaseCollection].aggregate(pipeline).to_list(length=None)
  debug(config,count)
  return {
    "count": count[0]['count']
  }
