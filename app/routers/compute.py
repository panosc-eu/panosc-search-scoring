#
# this file contains all the code implementing the compute endpoint of FPS
#

# importing libraries
from fastapi import APIRouter
from datetime import datetime

from ..models.compute import ComputeStatusModel
from ..common.utils import getCurrentTimestamp

# instantiate the fastapi router object
router = APIRouter(
  prefix='/compute',
  tags=['compute']
)

# GET:/compute
# return information on the weight computation
@router.get('/')
async def get_compute_info(response_model=ComputeStatusModel):
  return {
    "requested" : getCurrentTimestamp(),
    "inProgress" : False 
  }

@router.post('/')
async def start_compute(response_model=ComputeStatusModel):
  return {
    "requested" : getCurrentTimestamp(),
    "started" : getCurrentTimestamp(),
    "inProgress" : True 
  }
