# testing suite for Panosc Search Scoring
# endpoints: none
# notes: test the weight computation
#  

from operator import itemgetter
from app.models.weights import WeightModel
from app.models.tf import TfModel
from app.models.idf import IdfModel
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
#from app.routers import compute as computeRouter
from app.routers import items as itemsRouter
#from app.routers import weights as weightsRouter
from test.pss_test_base import pss_test_base
from app.models.compute import ComputeStatusModel,ComputeStatusResponseModel
from app.common.database import COLLECTION_ITEMS, COLLECTION_STATUS, COLLECTION_TF, COLLECTION_IDF


class TestWeightsComputation(pss_test_base):

  # define test database
  _db_database_uri = test_data.test_database_uri
  _db_database_name = test_data.test_database
  # define collection we want to work with
  _endpoint_name = itemsRouter.endpointRoute
  _data = test_data.test_items_terms
  # initial status needed for the test
  # check in test data for possible values
  _initial_status = 'not_run_yet'


  # properties needed to test class instance
  _wc_test_data = None
  _wc_config = None
  _wc_database = None
  _wc_items_collection = None
  _wc_status_collection = None
  _wc_tf_collection = None 
  _wc_idf_collection = None 
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
    self._db_collection = self._db_database[COLLECTION_STATUS]
    self._data = test_data.test_status
    res1 = super()._populateDatabase(itemKey=self._initial_status)

    # first inserts items
    self._db_collection = self._db_database[COLLECTION_ITEMS]
    self._data = test_data.test_items_terms
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
    self._wc_items_collection = self._wc_database[COLLECTION_ITEMS]
    self._wc_status_collection = self._wc_database[COLLECTION_STATUS]
    self._wc_tf_collection = self._wc_database[COLLECTION_TF]
    self._wc_idf_collection = self._wc_database[COLLECTION_IDF]

    # create index on weights collection
    self._wc_idf_collection.create_index(
      [
        ("group", pymongo.ASCENDING),
        ("term", pymongo.ASCENDING)
      ],
      unique=True
    )
    # obtains list of groups from test data
    self._wc_groups_list = list(set([
      item['group'] if 'group' in item.keys() else 'default'
      for item 
      in test_data.test_items_terms.values()
    ]))
    #self._wc_selected_group = [item for item in self._wc_groups_list if item != 'default'][0]
    self._wc_selected_group = self._wc_groups_list[0]
    # items and ids of the group
    self._wc_group_items = [
      item 
      for item 
      in test_data.test_items_terms.values() 
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
      self._wc_tf_collection,
      self._wc_idf_collection
    )
    # test properties
    assert wc._config == self._wc_config
    assert wc._db == self._wc_database
    assert wc._items_coll == self._wc_items_collection
    assert wc._status_coll == self._wc_status_collection
    assert wc._tf_coll == self._wc_tf_collection 
    assert wc._idf_coll == self._wc_idf_collection 


  # list groups
  @pytest.mark.asyncio
  async def test_list_groups(self):
    print("test_weight_computation.test_list_group")
    # set initial status
    self._initial_status = 'in_progress'
    # insert a items to be scored
    self._initialize_environment_for_class_test()
    #db_status = await self._wc_status_collection.find_one()
    #print("test list group ---------------------------")
    #print(db_status)
    #print("test list group ---------------------------")
    # instantiate class
    wc = WC(
      self._wc_config, 
      self._wc_database, 
      self._wc_items_collection, 
      self._wc_status_collection, 
      self._wc_tf_collection,
      self._wc_idf_collection
    )
    # retrieve group list
    wc_groups_list = await wc.groups_list()
    #print(wc_groups_list)
    # test list
    assert sorted(wc_groups_list) == sorted(self._wc_groups_list)
    # check status
    db_status = await self._wc_status_collection.find_one()
    #print(db_status)
    # check that the status is the final status
    assert db_status['progressPercent'] == 0.06
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
      self._wc_tf_collection,
      self._wc_idf_collection
    )
    # select group
    print(self._wc_selected_group)
    await wc.select_group(self._wc_selected_group)
    # test group
    assert wc._group == self._wc_selected_group
    # check status
    db_status = await self._wc_status_collection.find_one()
    # check that the status is the final status
    assert db_status['progressPercent'] == 0.10
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
      self._wc_tf_collection,
      self._wc_idf_collection
    )
    # select group
    await wc.select_group(self._wc_selected_group)
    # invoke load method
    await wc.load_items()
    # check values loaded
    # they are in a pandas dataframe
    #
    # first number of elements
    assert len(wc._items_to_be_updated) == len(self._wc_group_items)
    # check items id
    wc_items_ids = list(set([item['itemId'] for item in wc._items_to_be_updated]))
    assert sorted(wc_items_ids) == sorted(self._wc_group_items_ids)
    # check status
    db_status = await self._wc_status_collection.find_one()
    # check that the status is the final status
    assert db_status['progressPercent'] == 0.16
    assert db_status['started'] is not None
    assert db_status['ended'] is None
    assert db_status['inProgress'] is True


  # check terms
  @pytest.mark.asyncio
  async def test_check_terms(self):
    print("test_weight_computation.test_check_terms")
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
      self._wc_tf_collection,
      self._wc_idf_collection
    )
    # prepare for extract
    await wc.select_group(self._wc_selected_group)
    await wc.load_items()
    # check if the key terms has been created in all the items
    is_key_terms_present = ['terms' in item.keys() for item in wc._items_to_be_updated]
    assert all( is_key_terms_present)
    # check if we have empty cell in the column
    terms_extracted = [len(item['terms']) > 0 for item in wc._items_to_be_updated]
    assert all(terms_extracted)
    # check status
    db_status = await self._wc_status_collection.find_one()
    # check that the status is the final status
    assert db_status['progressPercent'] == 0.16
    assert db_status['started'] is not None
    assert db_status['ended'] is None
    assert db_status['inProgress'] is True


  # compute
  @pytest.mark.asyncio
  async def test_compute_tf_weights(self):
    print("test_weight_computation.test_compute_tf_weight")
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
      self._wc_tf_collection,
      self._wc_idf_collection
    )
    # prepare for this test
    await wc.select_group(self._wc_selected_group)
    await wc.load_items()
    print(wc._items_to_be_updated[0:5])
    # invoke compute method
    await wc.compute_TF()
    # check that something was saved in the weights place holder
    print(wc._TF)
    assert wc._TF is not None
    # check that rows match the items id
    TF_items_ids = [item[1] for item in wc._TF_rows]
    assert sorted(TF_items_ids) == sorted(self._wc_group_items_ids)
    # check that there is at least one weights that are greater than zero
    assert len(wc._TF.data) > 0
    # check status
    db_status = await self._wc_status_collection.find_one()
    # check that the status is the final status
    assert db_status['progressPercent'] == 0.21
    assert db_status['started'] is not None
    assert db_status['ended'] is None
    assert db_status['inProgress'] is True


  # save
  @pytest.mark.asyncio
  async def test_save_TF_weights(self):
    print("test_weight_computation.test_save_TF_weight")
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
      self._wc_tf_collection,
      self._wc_idf_collection
    )
    # select group
    await wc.select_group(self._wc_selected_group)
    # prepare for this test
    await wc.load_items()
    await wc.compute_TF()
    # invoke save method
    await wc.save_TF()
    # find weights matrix size
    wc_number_of_tf_weights = wc._TF.shape[0] * wc._TF.shape[1]
    # find number of non zero elements that we are expecting in the collection
    wc_number_of_non_zero_tf_weights = len(wc._TF.data)
    # count weights in collection
    db_number_of_tf_weights = await self._wc_tf_collection.count_documents({})
    # check that something was saved in the weights place holder
    assert wc_number_of_tf_weights >= db_number_of_tf_weights
    assert wc_number_of_non_zero_tf_weights == db_number_of_tf_weights
    assert db_number_of_tf_weights > 0
    # check status
    db_status = await self._wc_status_collection.find_one()
    # check that the status is the final status
    assert db_status['progressPercent'] == 0.27
    assert db_status['started'] is not None
    assert db_status['ended'] is None
    assert db_status['inProgress'] is True
    

  # delete all IDF
  @pytest.mark.asyncio
  async def test_delete_all_IDF_weights(self):
    print("test_weight_computation.test_delte_all_IDF_weights")
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
      self._wc_tf_collection,
      self._wc_idf_collection
    )
    # select group
    await wc.select_group(self._wc_selected_group)
    # prepare for this test
    await wc.load_items()
    await wc.compute_TF()
    await wc.save_TF()
    # caall the delete all method for IDF
    await wc.delete_all_IDF()
    # count idf weights in collection
    db_number_of_idf_weights = await self._wc_idf_collection.count_documents({})
    # check that there are no IDF weights in the collection
    assert db_number_of_idf_weights == 0
    # check status
    db_status = await self._wc_status_collection.find_one()
    # check that the status is the final status
    assert db_status['progressPercent'] == 0.51
    assert db_status['started'] is not None
    assert db_status['ended'] is None
    assert db_status['inProgress'] is True


  # compute and save IDF
  @pytest.mark.asyncio
  async def test_compute_and_save_IDF_weights(self):
    print("test_weight_computation.test_compute_and_save_IDF_weights")
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
      self._wc_tf_collection,
      self._wc_idf_collection
    )
    # select group
    await wc.select_group(self._wc_selected_group)
    # prepare for this test
    await wc.load_items()
    await wc.compute_TF()
    await wc.save_TF()
    await wc.delete_all_IDF()
    # caall the delete all method for IDF
    await wc.compute_and_save_IDF()
    # computes how many IDF weights we should expect
    # which is the number of terms (aka columns in the TF matrix) 
    wc_number_of_idf_weights = len(wc._TF_cols)
    # count idf weights in collection
    db_number_of_idf_weights = await self._wc_idf_collection.count_documents({})
    # check that there are no IDF weights in the collection
    assert db_number_of_idf_weights == wc_number_of_idf_weights
    # check status
    db_status = await self._wc_status_collection.find_one()
    # check that the status is the final status
    assert db_status['progressPercent'] == 0.61
    assert db_status['started'] is not None
    assert db_status['ended'] is None
    assert db_status['inProgress'] is True



  # run offline workflow
  @pytest.mark.asyncio
  async def test_run_offline_workflow(self):
    print("test_weight_computation.test_run_offline_workflow")
    # set initial status
    self._initial_status = 'requested'
    # insert a items to be scored
    self._initialize_environment_for_class_test()
    # instantiate class
    wc = await WC.runOfflineWorkflow(
      self._wc_config, 
      self._wc_database
    )
    # count weights in collection
    db_number_of_tf_weights = await self._wc_tf_collection.count_documents({})
    db_number_of_idf_weights = await self._wc_idf_collection.count_documents({})
    # check that something was saved in the weights place holder
    assert db_number_of_tf_weights > 0
    assert db_number_of_idf_weights > 0
    # check one TF weight to match the model
    db_tf_weight = await self._wc_tf_collection.find_one()
    print(db_tf_weight)
    try:
      db_tf_weight_model = TfModel(**db_tf_weight)
      assert True
    except:
      assert False
    # check one IDF weight to match the model
    db_idf_weight = await self._wc_idf_collection.find_one()
    print(db_idf_weight)
    try:
      db_idf_weight_model = IdfModel(**db_idf_weight)
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



  # run online workflow
  @pytest.mark.asyncio
  async def test_run_online_workflow(self):
    print("test_weight_computation.test_run_online_workflow")
    # set initial status
    self._initial_status = 'requested'
    # insert a items to be scored
    self._initialize_environment_for_class_test()
    # run offline workflow to populate weights
    wc = await WC.runOfflineWorkflow(
      self._wc_config, 
      self._wc_database
    )
    # retrieve few tf and idf weights for comparison
    db_tf_weights_1 = {}
    db_idf_weights_1 = {}
    db_terms_1 = {}
    for group in self._wc_groups_list:
      db_tf_weights_1[group] = await self._wc_tf_collection.find({'group' : group}).to_list(None)
      db_idf_weights_1[group] = await self._wc_idf_collection.find({'group' : group}).to_list(None)
      db_terms_1[group] = await self._wc_tf_collection.find(
        filter = {'group': group},
        projection = {'term'}
      ).to_list(None)
    # check status
    db_status = await self._wc_status_collection.find_one()
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
    
    
    # run online workflow removing 2 items of group group_1
    work_items_id = [
      i['id'].lower()
      for k,i
      in self._data.items()
      if k in ['item_3','item_5']
    ]
    work_items = [
      self._prepItemForInsertion(i)
      for i
      in self._wc_test_data
      if i['id'] in work_items_id
    ]

    # trigger online workflow with items removed
    # remove items selected
    await self._wc_items_collection.delete_many({'_id' :{ '$in' : work_items_id }})

    wc = await WC.runIncrementalWorkflow(
      self._wc_config,
      self._wc_database,
      delete_items=work_items_id
    )
    # retrieve new TF and IDF and compare them with previous
    db_tf_weights_2 = {}
    db_idf_weights_2 = {}
    db_terms_2 = {}
    for group in self._wc_groups_list:
      db_tf_weights_2[group] = await self._wc_tf_collection.find({'group' : group}).to_list(None)
      db_idf_weights_2[group] = await self._wc_idf_collection.find({'group' : group}).to_list(None)
      db_terms_2[group] = await self._wc_tf_collection.find(
        filter = {'group': group},
        projection = {'term'}
      ).to_list(None)
    # first we check that the weights for group default are the same
    assert db_tf_weights_1['default'] == db_tf_weights_2['default']
    assert db_idf_weights_1['default'] == db_idf_weights_2['default']
    # than we check that the weights for group group_1 are different
    assert db_tf_weights_1['group_1'] != db_tf_weights_2['group_1']
    assert db_idf_weights_1['group_1'] != db_idf_weights_2['group_1']
    # check status
    db_status = await self._wc_status_collection.find_one()
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
    

    # insert back the two items that were removed
    res = self._wc_items_collection.insert_many(work_items)

    # trigger online workflow with items re-added
    wc = await WC.runIncrementalWorkflow(
      self._wc_config,
      self._wc_database,
      new_items=work_items
    )
    # retrieve new TF and IDF and compare them with initial ones
    db_tf_weights_2 = {}
    db_idf_weights_2 = {}
    db_terms_2 = {}
    for group in self._wc_groups_list:
      db_tf_weights_2[group] = await self._wc_tf_collection.find({'group' : group}).to_list(None)
      db_idf_weights_2[group] = await self._wc_idf_collection.find({'group' : group}).to_list(None)
      db_terms_2[group] = await self._wc_tf_collection.find(
        filter = {'group': group},
        projection = {'term'}
      ).to_list(None)
    # first we check that the weights for group default are the same
    assert db_tf_weights_1['default'] == db_tf_weights_2['default']
    assert db_idf_weights_1['default'] == db_idf_weights_2['default']
    # than we check that the weights for group group_1 are different
    assert db_tf_weights_1['group_1'] == db_tf_weights_2['group_1']
    assert db_idf_weights_1['group_1'] == db_idf_weights_2['group_1']

    # check status
    db_status = await self._wc_status_collection.find_one()
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
