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
from app.common.database import COLLECTION_ITEMS, COLLECTION_TF, COLLECTION_IDF

endpointRoute = "weights"


# instantiate the fastapi router object
router = APIRouter(
  prefix='/' + endpointRoute,
  tags=[endpointRoute]
)


def _getAggregationPipeline(
    group=None,
    count=False 
):
  pipeline = [
    {
      '$project' : {
        '_id' :  0,
        'id' : { '$toString' : '$_id' },
        'term' : '$term',
        'timestamp' : '$timestamp',
        'TF' : '$TF',
        'itemId' : '$itemId',
        'group' : '$group'
      }
    }
  ]

  if group is not None:
    # user has provided the group we need to return
    pipeline.append(
      {
        '$match' : {
          'group' : group
        }
      }
    )

  if not count:
    pipeline += [
      {
        "$lookup" :{
          'from' : COLLECTION_IDF,
          'let' : { 'term' : '$term', 'group' : '$group' },
          'pipeline' : [
            {
              '$match' : {
                '$expr' : {
                  '$and' : [
                    { '$eq' : [ '$term' , '$$term' ]},
                    { '$eq' : [ '$group' , '$$group' ] }
                  ]
                }
              }
            }
          ],
          'as' : 'idf'
        }
      },
      {
        '$unwind' : '$idf'
      },
      {
        '$project' : {
          '_id' :  0,
          'id' : 1,
          'term' : 1,
          'timestamp' : 1,
          'TF' : 1,
          'itemId' : 1,
          'group' : 1,
          "IDF" : "$idf.IDF",
          "value" : { "$multiply" : [ "$TF", "$idf.IDF" ]}
        }
      }
    ]
  else:
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
    group
  )

  weights = await db[COLLECTION_TF].aggregate(pipeline).to_list(length=None)

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
    group,
    True
  )

  # retrieve results
  count = await db[COLLECTION_TF].aggregate(pipeline).to_list(length=None)
  
  return {
    "count": count[0]["count"] if len(count)>0 else 0
  }



