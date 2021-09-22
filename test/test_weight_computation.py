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


  # properties needed to test class instance
  _wc_test_data = None
  _wc_config = None
  _wc_database = None
  _wc_items_collection = None
  _wc_status_collection = None
  _wc_weights_collection = None 
  _wc_groups_list = None
  _wc_selected_group = None


  # auxiliary functions
  def _cleanTestData(self,inData):
    outData = deepcopy(inData[0])
    del outData['id']
    return outData


  #
  # set up environment for testing class methods
  def _initialize_environment_for_class_test(self):
    # now populate database
    self._wc_test_data = self._populateDatabase()
    # instantiate config class
    self._wc_config = Config()
    # instantiate database and collections
    db_client = AsyncIOMotorClient(config.mongodb_url)
    self._wc_database = db_client[config.database]
    self._wc_items_collection = db_database[itemsRouter.endpointRoute]
    self._wc_status_collection = db_database[computeRouter.endpointRoute]
    self._wc_weights_collection = db_database[weightsRouter.endpointRoute]
    # obtains list of groups from test data
    self._wc_groups_list = list(set([item['group'] for item in test_data.test_items.values()]))
    self._wc_selected_group = self._groups_list[0]
    # items and ids of the group
    self._wc_group_items = [item for item in test_data.test_items.values() if item['group'] == self._wc_selected_group]
    # check items id
    self._wc_items_ids = [item['_id'] for item in self._wc_group_items]


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
  def test_list_groups(self):
    print("test_weight_computation.test_list_group")
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
    wc_groups_list = wc.groups_list()
    # test list
    assert wc_groups_list == self._wc_groups_list
    # check status
    db_status = self._db_database[computeRouter.endpointRoute].find_one()
    # check that the status is the final status
    assert db_status['progressPercent'] == 0.02



  # select group
  def test_select_group(self):
    print("test_weight_computation.test_select_group")
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
    wc.select_group(self._wc_selected_group)
    # test group
    assert wc._group == self._wc_selected_group
    # check status
    db_status = self._db_database[computeRouter.endpointRoute].find_one()
    # check that the status is the final status
    assert db_status['progressPercent'] == 0.03


  # load
  def test_load_items(self):
    print("test_weight_computation.test_load_items")
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
    wc.select_group(self._wc_selected_group)
    # invoke load method
    wc.load()
    # check values loaded
    # they are in a pandas dataframe
    #
    # first number of elements
    assert len(wc._items) == len(self._wc_group_items)
    # check items id
    wc_items_ids = pd.unique(wc._items['_id'])
    assert wc_items_ids == self._wc_items_ids
    # check status
    db_status = self._db_database[computeRouter.endpointRoute].find_one()
    # check that the status is the final status
    assert db_status['progressPercent'] == 0.20


  # extract
  def test_extract_terms(self):
    print("test_weight_computation.test_extract_terms")
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
    wc.select_group(self._wc_selected_group)
    # load items
    wc.load()
    # invoke extract method
    wc.extract()
    # check if the new column terms has been created in the items dataframe
    assert 'terms' in wc._items.columns
    # check if we have empty cell in the column
    terms_extracted = wc._items.apply(lambda row: len(row['terms']) > 0, axis=1)
    assert terms_extracted.all()
    # check status
    db_status = self._db_database[computeRouter.endpointRoute].find_one()
    # check that the status is the final status
    assert db_status['progressPercent'] == 0.40


  # compute
  def test_compute_weights(self):
    print("test_weight_computation.test_compute_weight")
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
    wc.select_group(self._wc_selected_group)
    # prepare for this test
    wc.load()
    wc.extract()
    # invoke compute method
    wc.compute()
    # check that something was saved in the weights place holder
    assert wc._weights is not None
    # check that rows match the items id
    assert wc._weights.index == self._wc_items_ids
    # check that there are some weights that are greater than zero
    assert wc._weights[wc._weights > 0].count().sum() > 0
    # check status
    db_status = self._db_database[computeRouter.endpointRoute].find_one()
    # check that the status is the final status
    assert db_status['progressPercent'] == 0.60


  # save
  def test_save_weights(self):
    print("test_weight_computation.test_save_weight")
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
    wc.select_group(self._wc_selected_group)
    # prepare for this test
    wc.load()
    wc.extract()
    wc.compute()
    # invoke save method
    wc.save()
    # find number of elements that we are expecting in the collection
    wc_number_of_weights = len(wc._weights) * len(wc._weights.columns)
    # count weights in collection
    db_number_of_weights = self._db_database[weightsRouter.endpointRoute].count_documents()
    # check that something was saved in the weights place holder
    assert wc_number_of_weights == db_number_of_weights
    # check status
    db_status = self._db_database[computeRouter.endpointRoute].find_one()
    # check that the status is the final status
    assert db_status['progressPercent'] == 0.85
    

  # runWorkflow
  def test_run_workflow(self):
    print("test_weight_computation.test_run_workflow")
    # insert a items to be scored
    self._initialize_environment_for_class_test()
    # instantiate class
    wc = WC.runWorkflow(
      self._wc_config, 
      self._wc_database, 
      self._wc_items_collection, 
      self._wc_status_collection, 
      self._wc_weights_collection
    )
    # count weights in collection
    db_number_of_weights = self._db_database[weightsRouter.endpointRoute].count_documents()
    # check that something was saved in the weights place holder
    assert db_number_of_weights > 0
    # check one element to match the model
    db_weight = self._db_database[weightsRouter.endpointRoute].find_one()
    try:
      db_weight_model = WeightModel(**db_weight)
      assert True
    except:
      assert False
    # check status
    db_status = self._db_database[computeRouter.endpointRoute].find_one()
    # does it match the model
    try:
      db_status_model = ComputeStatusModel(**db_status)
      assert True
    except:
      assert False
    # check that the status is the final status
    assert db_status_model['progressPercent'] == 1.00



