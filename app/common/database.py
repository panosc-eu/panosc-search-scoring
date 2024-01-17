#
#
#

from typing import Callable

import pymongo
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi import FastAPI
from functools import partial

from .config import Config
from .utils import debug

#app_db_client: AsyncIOMotorClient = None
#app_db_database: AsyncIOMotorDatabase = None

COLLECTION_TF = 'weights_tf'
COLLECTION_IDF = 'weights_idf'
COLLECTION_ITEMS = 'items'
COLLECTION_STATUS = 'status'

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
    debug(config,app.state.db_database)

  return partial(db_connect, app=app)


def db_add_indexes_handler(app: FastAPI) -> Callable:
  """
  Make sure that the correct indexes exists
  """
  async def db_add_indexes(app: FastAPI) -> None:
    db = app.state.db_database

    coll = db["weights_idf"]
    indexes = await coll.index_information()
    if "weights_idf_group_name" not in indexes:
      coll.create_index(
        [
          ("group", pymongo.ASCENDING),
          ("term", pymongo.ASCENDING)
        ],
        name='weights_idf_group_name',
        unique=True
      )

  return partial(db_add_indexes, app=app)



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

