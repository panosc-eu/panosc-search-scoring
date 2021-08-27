#
# this file contains all the code implementing the score endpoint of FPS
#

# importing libraries
from fastapi import APIRouter
from ..models.score import ScoreRequestModel, ScoresOutputModel
# instantiate the fastapi router object
router = APIRouter(
  prefix='/score',
  tags=['score']
)

# Route POST:/score
@router.post("/")
async def get_scores(scoreRequest: ScoreRequestModel, response_model:ScoresOutputModel):
  return "Score is 0"
