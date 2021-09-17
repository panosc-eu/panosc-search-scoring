#
# this file contains all the code implementing the score endpoint of FPS
#

# importing libraries
from fastapi import APIRouter, Request

from ..models.score import ScoreRequestModel, ScoreResponseModel, ScoresResultsModel
from .weights import endpointRoute as weightsCollection
from .compute import endpointRoute as computeCollection

from ..ml.scorescomputation import SC


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
async def get_scores(req: Request, scoreRequest: ScoreRequestModel):
  pass# extract db and config from the app class
  config = req.app.state.config
  db = req.app.state.db_database

  # compute the scores
  oSC = await SC.runWorkflow(scoreRequest,db,db[weightsCollection])
  
  # check weight computation status
  computeStatus = await db[computeCollection].find({}).to_list(None)
  computeInProgress = computeStatus[0]['inProgress'] if len(computeStatus) > 0 else False

  return {
    'request': scoreRequest,
    'query' : {
      'query' : scoreRequest['query'],
      'terms' : oSC.getQueryTerms()
    },
    'scores' : oSC.getScores(),
    'dimensions' : oSC.getScoresLength(),
    'computeInProgress' : computeInProgress
  }

