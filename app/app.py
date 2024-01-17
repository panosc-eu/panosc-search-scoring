#import uvicorn
from _pytest.python_api import ApproxBase
from fastapi import FastAPI, Request

from .routers import items, compute, score, terms, weights
from .common import config, database

# instantiate local classes
appConfig = config.Config()

# instantiate main application
app = FastAPI(
  title=appConfig.application,
  description=appConfig.description,
  version=appConfig.version
)
app.state.config = appConfig
app.state.db_client = None
app.state.db_database = None
# instantiate database handler
app.add_event_handler("startup",database.db_connect_handler(app))
# make sure that the correct indexes are present
app.add_event_handler("startup",database.db_add_indexes_handler(app))
# close connection to database
app.add_event_handler("shutdown",database.db_close_handler(app))

# include individual subsystems endpoints
app.include_router(items.router)
app.include_router(compute.router)
app.include_router(score.router)
app.include_router(terms.router)
app.include_router(weights.router)

# implement root endpoint
# the purpose is to check if the server is operational
@app.get("/")
async def root():
  return appConfig.getCurrentRootInfo()

# Using Request instance
@app.get("/url-list")
def get_all_urls_from_request(request: Request):
    url_list = [
        {"path": route.path, "name": route.name} for route in request.app.routes
    ]
    return url_list


#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)
