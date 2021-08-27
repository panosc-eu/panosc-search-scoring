#
# database class

import motor.motor_asyncio as motor_asyncio


class Database:

  __client = None
  __db = None

  def __init__(self,config):
    self.__client = motor.AsyncIOMotorClient(config.mongodb_url)
    self.__db = self.__client[config.database]

  @property
  def client(self):
    return self.__client

  @property
  def db(self):
    return self.__db


from motor.motor_asyncio import AsyncIOMotorClient


db_client: AsyncIOMotorClient = None


async def get_db_client() -> AsyncIOMotorClient:
    """Return database client instance."""
    return db_client


async def connect_db():
    """Create database connection."""
    db_client = AsyncIOMotorClient(DB_URL)

async def close_db():
    """Close database connection."""
    db_client.close()
