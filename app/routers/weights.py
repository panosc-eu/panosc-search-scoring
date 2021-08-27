#
# this file contains all the code implementing the weights endpoint of FPS
#

# importing libraries
from datetime import datetime
from fastapi import APIRouter
from typing import List, Optional

from ..models.weights import WeightModel
from ..common.utils import getCurrentTimestamp

# instantiate the fastapi router object
router = APIRouter(
  prefix='/weights',
  tags=['weights']
)
  
# Route GET:/weights
@router.get("/")
async def get_terms(query: Optional[str] = None, group: Optional[str] = None, grouped: Optional[bool] = False, response_model=List[WeightModel]):
  return [
    WeightModel(
      term="Term 1",
      itemId="this_is_an_id",
      timestamp=getCurrentTimestamp(),
      value=0.0
    )
  ]
    
