#
# this file contains all the code implementing the score endpoint of FPS
#

# importing libraries
from fastapi import APIRouter, Request, Body, HTTPException
from fastapi.encoders import jsonable_encoder
import json

from app import common

from ..models.score import ScoreRequestModel, ScoreResponseModel, ScoresResultsModel
from .weights import endpointRoute as weightsCollection
from .compute import endpointRoute as computeCollection

from ..ml.scorescomputation import SC
from ..common.utils import debug


# main tag, route and database collection for compute
endpointRoute = "score"



# instantiate the fastapi router object
router = APIRouter(
  prefix='/' + endpointRoute,
  tags=[endpointRoute]
)


# Route POST:/score
@router.post(
  "",
  status_code=200,
  response_model=ScoreResponseModel 
)
async def get_scores(req: Request, scoreRequest = Body(...)):
#async def get_scores(req: Request, scoreRequest: ScoreRequestModel):
  # extract db and config from the app class
  config = req.app.state.config
  db = req.app.state.db_database

  try: 
    # check if we get a string in input. 
    # If that's the case, it will try to convert it to a python data type
    if type(scoreRequest) is str or type(scoreRequest) is bytes:
      debug(config,"Converting input to python type")
      scoreRequest = json.loads(scoreRequest)

    debug(config,ScoreRequestModel(**scoreRequest))

    debug(config,type(SC))
    # compute the scores
    oSC = await SC.runWorkflow(config,scoreRequest,db,db[weightsCollection])
    debug(config,oSC)
  
    # check weight computation status
    computeStatus = await db[computeCollection].find({}).to_list(None)
    computeInProgress = computeStatus[0]['inProgress'] if len(computeStatus) > 0 else False

    return {
      'request': jsonable_encoder(ScoreRequestModel(**scoreRequest)),
      'query' : {
        'query' : scoreRequest['query'],
        'terms' : oSC.getQueryTerms()
      },
      'scores' : oSC.getScores(),
      'dimension' : oSC.getScoresLength(),
      'computeInProgress' : computeInProgress,
      'started' : oSC.started,
      'ended' : oSC.ended
    }
  
  except Exception as e:
    raise HTTPException(
      status_code=400,
      detail="An exception of type {0} occurred. Arguments:\n{1!r}".format(type(e).__name__, e.args)
    )
