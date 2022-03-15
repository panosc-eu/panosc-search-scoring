# testing suite for Panosc Search Scoring
# all items endpoints
#  

from json.decoder import JSONDecodeError
from fastapi.testclient import TestClient
import pymongo
from copy import deepcopy


# abstract class
# needs to be inherited by a real class implementation 
class pss_test_base:

  # database connection information
  _db_database_uri = ""
  _db_database_name = ""
  _db_collection_name = ""
  # database object
  _db_client = None
  _db_database = None
  _db_collection = None
  # collection name
  # it needs to be defined in the 
  _endpoint_name = ""
  _endpoint_url = ""
  # test data
  _data = None

  # 
  @classmethod
  def setup_class(cls):
    print("PSS test class : setup class")
    print("Endpoints group : " + str(cls._endpoint_name))

    # connect to database
    cls._db_client = pymongo.MongoClient(cls._db_database_uri)
    #print(cls._db_client)
    #print(cls._db_database_name)
    cls._db_database = cls._db_client[cls._db_database_name]
    #print(cls._db_database)
    if not cls._db_collection_name:
      # database collection name has been left empty
      # so that means that the collection name is th esame as the endpoint name
      cls._db_collection_name = cls._endpoint_name

    #print(cls._db_collection_name)
    cls._db_collection = cls._db_database[cls._db_collection_name]
    #print(cls._db_collection)
    #print(cls._endpoint_name)
    cls._endpoint_url = "/" + cls._endpoint_name
    #print(cls._endpoint_url)


  #
  @classmethod
  def teardown_class(cls):
    print("PSS test class : teardown class")
    print("Endpoints group : " + cls._endpoint_name)


  # empty the database
  def _empty_database(self):
    print("PSS test class : empty database")

    # delete all the collections
    for coll_name in self._db_database.list_collection_names():
      print("Dropping collection : " + coll_name)
      temp_coll = self._db_database[coll_name]
      temp_coll.drop()


  # lowercase uuid
  def _lowercaseItemId(self,item):
    print("PSS test class : lowercase item id")
    if 'id' in item.keys():
      item['id'] = item['id'].lower()
    return item

  # prepare item to be inserted in database
  def _prepItemForInsertion(self,inItem):
    print("PSS test class : prep item for insertion")
    outItem = deepcopy(inItem)
    outItem['_id'] = outItem['id'].lower()
    del outItem['id']
    return outItem


  # create items in database
  def _populateDatabase(self, numberOfItems=-1, itemKey=None):
    """
    prepare test data and insert it in the database.
    Input:
      - numberOfItems (int): 
          select first numberOfItems in the list of data
          It takes precedence over itemKey                 
      - itemKey (str, int):
          Index of the element that we want to select
    """
    print("PSS test class : populate database")

    # copy data
    outData = deepcopy(self._data)

    if numberOfItems>0:
      # convert dict to list if necessary
      if isinstance(outData,dict):
        outData = list(outData.values())
    
      # select only first numberOfItems items
      outData = outData[0:numberOfItems]

    elif itemKey is not None:
      # select only the element with the key passed
      outData = [outData[itemKey]]

    else:
      # convert dict to list if necessary
      if isinstance(outData,dict):
        outData = list(outData.values())
    

    # takes care of normalizing uuid if they are uppercase
    outData = [
      self._lowercaseItemId(item)
      for item 
      in outData
    ]

    # insert items in collection
    res = self._db_collection.insert_many([
      self._prepItemForInsertion(item)
      for item 
      in outData
    ])
    #print(res.inserted_ids)

    return outData

  #
  def setup_method(self,method):
    print("PSS test class : setup method")
    self._empty_database()


  #
  def teardown_method(self,method):
    print("PSS test class : teardown method")
    self._empty_database()

