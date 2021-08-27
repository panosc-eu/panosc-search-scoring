#
# this file contains all the code implementing the terms endpoint of FPS
#

# importing libraries
from fastapi import APIRouter
from typing import Dict, List, Optional
from ..models.terms import TermListModel

# instantiate the fastapi router object
router = APIRouter(
  prefix='/terms',
  tags=['terms']
)
  
# Route GET:/terms
@router.get("/")
async def get_terms(query: Optional[str] = None, group: Optional[str] = None, grouped: Optional[bool] = False, response_model=List[TermListModel]):
  return [
    TermListModel(
      terms=["Term 1","Term 2","No more terms"]
    )
  ]
    
