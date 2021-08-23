#import uvicorn
from fastapi import FastAPI
from .routers import items
import datetime


tsStarted = datetime.datetime.now()
# configuration
config = {
  "application" : "PSS",
  "description" : "PaNOSC search scoring",
  "version" : "v1.0-alpha-1",
  "startedtime" : tsStarted 
}

# instantiate main application
app = FastAPI(
  title=config["application"],
  description=config["description"],
  version=config["version"]
)

# include individual subsystems endpoints
app.include_router(items.router)

# implement root endpoint
# the purpose is to check if the server is operational
@app.get("/")
async def root():
  tsCurrent = datetime.datetime.now()
  return { 
    **config,
    **{
      "currenttime" : tsCurrent.isoformat(),
      "uptime" : str(tsCurrent - tsStarted)
    }
  }

#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)
