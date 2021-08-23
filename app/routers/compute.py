#
# this file contains all the code implementing the compute endpoint of FPS
#

# importing libraries
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

# instantiate the fastapi router object
router = APIRouter(
  prefix='/compute',
  tags=['compute']
)

# compute info model
class ComputeInfo(BaseModel):
  requested: datetime
  started: Optional[datetime]
  ended: Optional[datetime]
  inProgress: bool

# GET:/compute
# return information on the weight computation
@router.get('/')
async def get_compute_info(response_model=ComputeInfo):
  return {
    "requested" : datetime.now,
    "inProgress" : False 
  }

@router.post('/')
async def start_compute(response_model=ComputeInfo):
  return {
    "requested" : datetime.now,
    "started" : datetime.now,
    "inProgress" : True 
  }
