#
# this file contains all the code implementing the weights endpoint of FPS
#

# importing libraries
from datetime import datetime
from fastapi import APIRouter, Request
from typing import List, Optional

from fastapi.encoders import jsonable_encoder

from ..models.weights import WeightResponseModel, WeightModel, WeightsCountResponseModel
from ..common.utils import getCurrentTimestamp
from .items import endpointRoute as itemCollection

endpointRoute = "weights"

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
        'id' : { '$toString' : '$_id' },
        'term' : '$term',
        'timestamp' : '$timestamp',
        'value' : '$value',
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

  if count:
    pipeline.append(
      {
        '$count' : 'count'
      }
    )

  return pipeline
 

# Route GET:/weights
@router.get(
  "",
  status_code=200,
  response_model=List[WeightResponseModel]
)
async def get_weights(
    req: Request,
    group: Optional[str] = None
):
  """
  return all the weights
  If groups is specified, anly the weights in the group are returned
  """
  # extract db and config from the app class
  config = req.app.state.config
  db = req.app.state.db_database

  # build aggregation pipeline
  pipeline = _getAggregationPipeline(
    itemCollection,
    group)

  weights = await db[endpointRoute].aggregate(pipeline).to_list(length=None)

  return jsonable_encoder(weights, by_alias=False)

    
# Route GET:/weights/count
@router.get(
  "/count", 
  response_model=WeightsCountResponseModel,
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

  # retrieve results
  count = await db[endpointRoute].aggregate(pipeline).to_list(length=None)

  return {
    "count": count[0]['count']
  }



