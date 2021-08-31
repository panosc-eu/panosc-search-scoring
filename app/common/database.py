#
#
#

from typing import Callable
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi import FastAPI
from functools import partial

from .config import Config

#app_db_client: AsyncIOMotorClient = None
#app_db_database: AsyncIOMotorDatabase = None


#def db_connect_handler(config: Config) -> Callable:
def db_connect_handler(app: FastAPI) -> Callable:
  """
    Create database connection.
  """
  async def db_connect(app: FastAPI) -> None:
    #global app_db_client
    #global app_db_database

    config = app.state.config
    #app_db_client = AsyncIOMotorClient(config.mongodb_url)
    #app_db_database = app_db_client[config.database]
    app.state.db_client = AsyncIOMotorClient(config.mongodb_url)
    app.state.db_database = app.state.db_client[config.database]

  return partial(db_connect, app=app)

#def db_close_handler() -> Callable:
def db_close_handler(app: FastAPI) -> Callable:
  """
    Close database connection.
  """
  async def db_close(app: FastAPI) -> None:
    #global app_db_client
    #global app_db_database

    #app_db_client.close()
    #app_db_database = None
    #app_db_client = None
    app.state.db_client.close()
    app.state.db_database = None
    app.state.db_client = None

  return partial(db_close,app=app)


async def get_database() -> AsyncIOMotorDatabase:
  global app_db_database

  #return app_db_database
  pass

