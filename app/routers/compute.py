#
# this file contains all the code implementing the compute endpoint of FPS
#

# importing libraries
from fastapi import APIRouter, Request, BackgroundTasks, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from datetime import datetime
from time import sleep

from starlette.responses import Response

from ..models.compute import ComputeStatusModel,ComputeStatusResponseModel
from ..common.utils import getCurrentIsoTimestamp, getCurrentTimestamp
from ..ml.weightscomputation import WC
from ..routers.items import endpointRoute as itemsCollectionName
from ..routers.weights import endpointRoute as weightsCollectionName


# main tag, route and database collection for compute
endpointRoute = "compute"

# instantiate the fastapi router object
router = APIRouter(
  prefix='/' + endpointRoute,
  tags=[endpointRoute]
)

# GET:/compute
# return information on the weight computation
@router.get(
  '',
  status_code=200,
  response_model=ComputeStatusResponseModel,
  responses={
    404: {
      'Model': ComputeStatusResponseModel
    },
    500: {
      'Model': { 'message' : str }
    }
  }
)
async def get_compute_status(
  req: Request
):
  # extract db and config from the app class
  config = req.app.state.config
  db = req.app.state.db_database

  # retrieve status from database
  # there should be only one, so we retrieve only one
  computeStatus = await db[endpointRoute].find({}).to_list(None)

  if not computeStatus or len(computeStatus) == 0:
    # item not found
    return JSONResponse(
      status_code=404,
      content=jsonable_encoder(
        ComputeStatusResponseModel(
          **{
            "progressPercent" : 0,
            "progressDescription" : "Weights computation not yet run",
            "inProgress" : False
          }
        )
      )
    )
  elif len(computeStatus) > 1:
    print("Found many status")
    print(computeStatus)
    # item not found
    return JSONResponse(
      status_code=500,
      content={'message' : 'multiple status entry in database'}
    )
  
  print("get_compute_status")
  print(computeStatus)
  return ComputeStatusResponseModel(**computeStatus[0])


#
async def run_background_weight_computation(config, db, coll):
  # wait few seconds
  sleep(config.waitToStartCompute)

  # update status in database
  res = await coll.update_many( 
    {}, 
    { 
      "$set" : { 
        "started" : getCurrentTimestamp(), 
        "inProgress" : True 
      }
    } 
  )

  # run the whole workflow
  wc = await WC.runWorkflow(
    config,
    db,
    itemsCollectionName,
    endpointRoute,
    weightsCollectionName)

  # update status in database
  res = await coll.update_many( 
    {}, 
    { 
      "$set" : { 
        "ended" : getCurrentTimestamp(), 
        "progressPercent" : 1,
        "progressDescription" : "Done",
        "inProgress" : False
      }
    } 
  )


#
@router.post(
  '',
  status_code=200,
  response_model=ComputeStatusResponseModel,
  responses={
    409: {
      'Model': ComputeStatusResponseModel
    },
    500: {
      'Model': { 'message' : str }
    }
  }
)
async def start_compute(
  req: Request,
  res: Response,
  background_tasks: BackgroundTasks
):
  # extract db and config from the app class
  config = req.app.state.config
  db = req.app.state.db_database

  triggerCompute = True

  # check if computation is already running
  computeStatuses = await db[endpointRoute].find({}).to_list(1000)
  if len(computeStatuses) > 1:
    # there are more than one status entries
    return JSONResponse(
      status_code=500,
      content={'message' : 'multiple status entry in database'}
    )
  elif computeStatuses:
    # status is present
    computeStatus = computeStatuses[0]

    # check if there is a compute already running
    if computeStatus['inProgress']:
      # compute already in progress
      # returns current status
      triggerCompute = False
      res.status_code = status.HTTP_409_CONFLICT
    else:
      # no active compute
      # remove previous entry
      lres = await db[endpointRoute].delete_many({})

  
  if triggerCompute:
    # we are good to go to start a new compute

    # prepare status entry
    computeStatus = jsonable_encoder(ComputeStatusModel(**{
      'requested' : getCurrentTimestamp(),
      'inProgress' : True
    }))

    # insert new status in db
    res = await db[endpointRoute].insert_one(computeStatus)

    # start computation in the background
    background_tasks.add_task(
      run_background_weight_computation,
      config,
      db,
      db[endpointRoute]
    )


  # return status
  return ComputeStatusResponseModel(**computeStatus)
