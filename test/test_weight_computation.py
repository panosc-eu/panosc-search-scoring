# testing suite for Panosc Search Scoring
# endpoints: none
# notes: test the weight computation
#  

from app.models.weights import WeightModel
from json.decoder import JSONDecodeError
from fastapi.testclient import TestClient
import pymongo
import datetime
import pytest
from copy import deepcopy
from mock import AsyncMock, Mock, patch
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import pandas as pd

#from app import app
from app.common.config import Config
from app.ml.weightscomputation import WC
import test.test_data as test_data
from app.routers import compute as computeRouter
from app.routers import items as itemsRouter
from app.routers import weights as weightsRouter
from test.pss_test_base import pss_test_base
from app.models.compute import ComputeStatusModel,ComputeStatusResponseModel


class TestWeightsComputation(pss_test_base):

  # define test database
  _db_database_uri = test_data.test_database_uri
  _db_database_name = test_data.test_database
  # define collection we want to work with
  _endpoint_name = itemsRouter.endpointRoute
  _data = test_data.test_items
  # initial status needed for the test
  # check in test data for possible values
  _initial_status = 'not_run_yet'


  # properties needed to test class instance
  _wc_test_data = None
  _wc_config = None
  _wc_database = None
  _wc_items_collection = None
  _wc_status_collection = None
  _wc_weights_collection = None 
  _wc_groups_list = None
  _wc_selected_group = None
  _wc_group_items = None
  _wc_group_items_ids = None


  # auxiliary functions
  def _cleanTestData(self,inData):
    outData = deepcopy(inData[0])
    del outData['id']
    return outData


  # overload populate database 
  # we need to insert items and weights
  def _populateDatabase(self):
    # insert status
    self._db_collection = self._db_database[computeRouter.endpointRoute]
    self._data = test_data.test_status
    res1 = super()._populateDatabase(itemKey=self._initial_status)

    # first inserts items
    self._db_collection = self._db_database[itemsRouter.endpointRoute]
    self._data = test_data.test_items
    res2 = super()._populateDatabase()

    return res2


  #
  # set up environment for testing class methods
  def _initialize_environment_for_class_test(self):
    # now populate database
    self._wc_test_data = self._populateDatabase()
    # instantiate config class
    self._wc_config = Config()
    # instantiate database and collections
    db_client = AsyncIOMotorClient(self._wc_config.mongodb_url)
    self._wc_database = db_client[self._wc_config.database]
    self._wc_items_collection = self._wc_database[itemsRouter.endpointRoute]
    self._wc_status_collection = self._wc_database[computeRouter.endpointRoute]
    self._wc_weights_collection = self._wc_database[weightsRouter.endpointRoute]
    # obtains list of groups from test data
    self._wc_groups_list = list(set([
      item['group'] if 'group' in item.keys() else 'default'
      for item 
      in test_data.test_items.values()
    ]))
    #self._wc_selected_group = [item for item in self._wc_groups_list if item != 'default'][0]
    self._wc_selected_group = self._wc_groups_list[0]
    # items and ids of the group
    self._wc_group_items = [
      item 
      for item 
      in test_data.test_items.values() 
      if ('group' in item.keys() and item['group'] == self._wc_selected_group) \
        or ( self._wc_selected_group == 'default' and 'group' not in item.keys() )
    ]
    # check items id
    self._wc_group_items_ids = [item['id'].lower() for item in self._wc_group_items]


  # 
  # TESTS
  # ================
  # instantiate WC class
  def test_instantiate_wc(self):
    print("test_weight_computation.test_instantiate_wc")
    # insert a items to be scored
    self._initialize_environment_for_class_test()
    # instantiate class
    wc = WC(
      self._wc_config, 
      self._wc_database, 
      self._wc_items_collection, 
      self._wc_status_collection, 
      self._wc_weights_collection
    )
    # test properties
    assert wc._config == self._wc_config
    assert wc._db == self._wc_database
    assert wc._items_coll == self._wc_items_collection
    assert wc._status_coll == self._wc_status_collection
    assert wc._weights_coll == self._wc_weights_collection 


  # list groups
  @pytest.mark.asyncio
  async def test_list_groups(self):
    print("test_weight_computation.test_list_group")
    # set initial status
    self._initial_status = 'in_progress'
    # insert a items to be scored
    self._initialize_environment_for_class_test()
    # instantiate class
    wc = WC(
      self._wc_config, 
      self._wc_database, 
      self._wc_items_collection, 
      self._wc_status_collection, 
      self._wc_weights_collection
    )
    # retrieve group list
    wc_groups_list = await wc.groups_list()
    print(wc_groups_list)
    # test list
    assert sorted(wc_groups_list) == sorted(self._wc_groups_list)
    # check status
    db_status = await self._wc_status_collection.find_one()
    # check that the status is the final status
    assert db_status['progressPercent'] == 0.03
    assert db_status['started'] is not None
    assert db_status['ended'] is None
    assert db_status['inProgress'] is True



  # select group
  @pytest.mark.asyncio
  async def test_select_group(self):
    print("test_weight_computation.test_select_group")
    # set initial status
    self._initial_status = 'in_progress'
    # insert a items to be scored
    self._initialize_environment_for_class_test()
    # instantiate class
    wc = WC(
      self._wc_config, 
      self._wc_database, 
      self._wc_items_collection, 
      self._wc_status_collection, 
      self._wc_weights_collection
    )
    # select group
    print(self._wc_selected_group)
    await wc.select_group(self._wc_selected_group)
    # test group
    assert wc._group == self._wc_selected_group
    # check status
    db_status = await self._wc_status_collection.find_one()
    # check that the status is the final status
    assert db_status['progressPercent'] == 0.05
    assert db_status['started'] is not None
    assert db_status['ended'] is None
    assert db_status['inProgress'] is True


  # load
  @pytest.mark.asyncio
  async def test_load_items(self):
    print("test_weight_computation.test_load_items")
    # set initial status
    self._initial_status = 'in_progress'
    # insert a items to be scored
    self._initialize_environment_for_class_test()
    # instantiate class
    wc = WC(
      self._wc_config, 
      self._wc_database, 
      self._wc_items_collection, 
      self._wc_status_collection, 
      self._wc_weights_collection
    )
    # select group
    await wc.select_group(self._wc_selected_group)
    # invoke load method
    await wc.load()
    # check values loaded
    # they are in a pandas dataframe
    #
    # first number of elements
    assert len(wc._items) == len(self._wc_group_items)
    # check items id
    wc_items_ids = list(set([item['_id'] for item in wc._items]))
    assert sorted(wc_items_ids) == sorted(self._wc_group_items_ids)
    # check status
    db_status = await self._wc_status_collection.find_one()
    # check that the status is the final status
    assert db_status['progressPercent'] == 0.20
    assert db_status['started'] is not None
    assert db_status['ended'] is None
    assert db_status['inProgress'] is True


  # extract
  @pytest.mark.asyncio
  async def test_extract_terms(self):
    print("test_weight_computation.test_extract_terms")
    # set initial status
    self._initial_status = 'in_progress'
    # insert a items to be scored
    self._initialize_environment_for_class_test()
    # instantiate class
    wc = WC(
      self._wc_config, 
      self._wc_database, 
      self._wc_items_collection, 
      self._wc_status_collection, 
      self._wc_weights_collection
    )
    # prepare for extract
    await wc.select_group(self._wc_selected_group)
    await wc.load()
    print(wc._items)
    # invoke extract method
    await wc.extract()
    # check if the key terms has been created in all the items
    is_key_terms_present = ['terms' in item.keys() for item in wc._items]
    assert all( is_key_terms_present)
    # check if we have empty cell in the column
    terms_extracted = [len(item['terms']) > 0 for item in wc._items]
    assert all(terms_extracted)
    # check status
    db_status = await self._wc_status_collection.find_one()
    # check that the status is the final status
    assert db_status['progressPercent'] == 0.40
    assert db_status['started'] is not None
    assert db_status['ended'] is None
    assert db_status['inProgress'] is True


  # compute
  @pytest.mark.asyncio
  async def test_compute_weights(self):
    print("test_weight_computation.test_compute_weight")
    # set initial status
    self._initial_status = 'in_progress'
    # insert a items to be scored
    self._initialize_environment_for_class_test()
    # instantiate class
    wc = WC(
      self._wc_config, 
      self._wc_database, 
      self._wc_items_collection, 
      self._wc_status_collection, 
      self._wc_weights_collection
    )
    # prepare for this test
    await wc.select_group(self._wc_selected_group)
    await wc.load()
    await wc.extract()
    print(wc._items[0:5])
    # invoke compute method
    await wc.compute()
    # check that something was saved in the weights place holder
    print(wc._weights)
    assert wc._weights is not None
    # check that rows match the items id
    assert sorted(wc._weights_rows) == sorted(self._wc_group_items_ids)
    # check that there is at least one weights that are greater than zero
    assert len(wc._weights.data) > 0
    # check status
    db_status = await self._wc_status_collection.find_one()
    # check that the status is the final status
    assert db_status['progressPercent'] == 0.60
    assert db_status['started'] is not None
    assert db_status['ended'] is None
    assert db_status['inProgress'] is True


  # save
  @pytest.mark.asyncio
  async def test_save_weights(self):
    print("test_weight_computation.test_save_weight")
    # set initial status
    self._initial_status = 'in_progress'
    # insert a items to be scored
    self._initialize_environment_for_class_test()
    # instantiate class
    wc = WC(
      self._wc_config, 
      self._wc_database, 
      self._wc_items_collection, 
      self._wc_status_collection, 
      self._wc_weights_collection
    )
    # select group
    await wc.select_group(self._wc_selected_group)
    # prepare for this test
    await wc.load()
    await wc.extract()
    await wc.compute()
    # invoke save method
    await wc.save()
    # find weights matrix size
    wc_number_of_weights = wc._weights.shape[0] * wc._weights.shape[1]
    # find number of non zero elements that we are expecting in the collection
    wc_number_of_non_zero_weights = len(wc._weights.data)
    # count weights in collection
    db_number_of_weights = await self._wc_weights_collection.count_documents({})
    # check that something was saved in the weights place holder
    assert wc_number_of_weights >= db_number_of_weights
    assert wc_number_of_non_zero_weights == db_number_of_weights
    assert db_number_of_weights > 0
    # check status
    db_status = await self._wc_status_collection.find_one()
    # check that the status is the final status
    assert db_status['progressPercent'] == 0.90
    assert db_status['started'] is not None
    assert db_status['ended'] is None
    assert db_status['inProgress'] is True
    

  # runWorkflow
  @pytest.mark.asyncio
  async def test_run_workflow(self):
    print("test_weight_computation.test_run_workflow")
    # set initial status
    self._initial_status = 'requested'
    # insert a items to be scored
    self._initialize_environment_for_class_test()
    # instantiate class
    wc = await WC.runWorkflow(
      self._wc_config, 
      self._wc_database, 
      self._wc_items_collection, 
      self._wc_status_collection, 
      self._wc_weights_collection
    )
    # count weights in collection
    db_number_of_weights = await self._wc_weights_collection.count_documents({})
    # check that something was saved in the weights place holder
    assert db_number_of_weights > 0
    # check one element to match the model
    db_weight = await self._wc_weights_collection.find_one()
    print(db_weight)
    try:
      db_weight_model = WeightModel(**db_weight)
      assert True
    except:
      assert False
    # check status
    db_status = await self._wc_status_collection.find_one()
    print(db_status)
    # does it match the model
    try:
      db_status_model = ComputeStatusModel(**db_status)
      assert True
    except:
      assert False
    # check that the status is the final status
    assert db_status['progressPercent'] == 1.00
    assert db_status['started'] is not None
    assert db_status['ended'] is not None
    assert db_status['inProgress'] is False


