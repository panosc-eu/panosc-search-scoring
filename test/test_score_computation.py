# testing suite for Panosc Search Scoring
# endpoints: none
# notes: test the weight computation
#  

from app.common.database import COLLECTION_TF, COLLECTION_IDF
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
from app.ml.scorescomputation import SC
import test.test_data as test_data
from app.routers import score as scoresRouter
from app.routers import weights as weightsRouter
from test.pss_test_base import pss_test_base
from app.models.score import ScoreRequestModel


class TestScoresComputation(pss_test_base):

  # define test database
  _db_database_uri = test_data.test_database_uri
  _db_database_name = test_data.test_database
  _db_collection_name = weightsRouter.endpointRoute
  # define collection we want to work with
  _endpoint_name = scoresRouter.endpointRoute
  #_data = list(test_data.test_weights.values())
  _data = None


  # properties needed to test class instance
  _sc_test_data = None
  _sc_score_request_dict = None
  _sc_score_request_model = None
  _sc_config = None
  _sc_database = None  
  _sc_tf_collection = None 
  _sc_idf_collection = None 
  #_sc_items_collection = None
  #_sc_status_collection = None
  #_sc_weights_collection = None 
  #_wc_groups_list = None
  #_wc_selected_group = None
  #_wc_group_items = None
  #_wc_group_items_ids = None


  # overload lowercase id, so we can take care of the item id also
  def _lowercaseItemId(self,item):
    print("PSS test weights : lowercase item ids")
    if 'id' in item.keys():
      item['id'] = item['id'].lower()
    if 'itemId' in item.keys():
      item['itemId'] = item['itemId'].lower()
    return item
  
  # overload populate database 
  # we need to insert items and weights
  def _populateDatabase(self):
    # insert tf
    self._db_collection = self._db_database[COLLECTION_TF]
    self._data = test_data.test_weights_tf
    res1 = super()._populateDatabase()

    # insert idf
    self._db_collection = self._db_database[COLLECTION_IDF]
    self._data = test_data.test_weights_idf
    res2 = super()._populateDatabase()

    return res2
  #
  # set up environment for testing class methods
  def _initialize_environment_for_class_test(self):
    # now populate database
    self._sc_test_data = self._populateDatabase()
    # query 
    self._sc_query = 'retrieval and information'
    self._sc_query_terms = ['retriev', 'inform']
    # item ids
    self._sc_items_ids = [
      (
        item['group'],
        item['itemId'].lower() 
      )
      for item 
      in test_data.test_scores_computation
    ]
    # create a score request as dictionary
    self._sc_score_request_dict = {
      'query': self._sc_query,
      'itemIds': [i[1] for i in self._sc_items_ids],
      'group' : "",
      'limit' : -1
    }
    # same request as Model
    self.sc_score_request_model = ScoreRequestModel(**self._sc_score_request_dict)

    # instantiate config class
    self._sc_config = Config()
    # instantiate database and collections
    db_client = AsyncIOMotorClient(self._sc_config.mongodb_url)
    self._sc_database = db_client[self._sc_config.database]
    self._sc_tf_collection = self._sc_database[COLLECTION_TF]
    self._sc_idf_collection = self._sc_database[COLLECTION_IDF]
    #  obtains list of groups from test data
    #self._wc_groups_list = list(set([
      #item['group'] if 'group' in item.keys() else 'default'
      #for item 
      #in test_data.test_items.values()
    #]))
    #self._wc_selected_group = [item for item in self._wc_groups_list if item != 'default'][0]
    #self._wc_selected_group = self._wc_groups_list[0]
    # items and ids of the group
    #self._wc_group_items = [
    #  item 
    #  for item 
    #  in test_data.test_items.values() 
    #  if ('group' in item.keys() and item['group'] == self._wc_selected_group) \
    #    or ( self._wc_selected_group == 'default' and 'group' not in item.keys() )
    #]
    # check items id
    #self._wc_group_items_ids = [item['id'].lower() for item in self._wc_group_items]


  # 
  # TESTS
  # ================
  # instantiate SC class
  def test_instantiate_sc(self):
    print("test_score_computation.test_instantiate_sc")
    # insert a items to be scored
    self._initialize_environment_for_class_test()
    # instantiate class
    sc = SC(
      self._sc_config,
      self._sc_score_request_dict,
      self._sc_database, 
      self._sc_tf_collection,
      self._sc_idf_collection
    )
    # test properties
    assert sc._request == self._sc_score_request_dict
    assert sc._db == self._sc_database
    assert sc._tf_coll == self._sc_tf_collection 
    assert sc._idf_coll == self._sc_idf_collection 


  # extract terms from query
  @pytest.mark.asyncio
  async def test_extract_query_terms(self):
    print("test_score_computation.test_extract_query_terms")
    # insert a items to be scored
    self._initialize_environment_for_class_test()
    # instantiate class
    sc = SC(
      self._sc_config,
      self._sc_score_request_dict,
      self._sc_database, 
      self._sc_tf_collection,
      self._sc_idf_collection
    )
    # extract query terms
    #print(sc)
    await sc._extract_query_terms()
    #print(sc._query_terms)
    # test list
    assert sc._query_terms.sort() == self._sc_query_terms.sort()


  # load weights
  @pytest.mark.asyncio
  async def test_load_weights(self):
    print("test_score_computation.test_load_weights")
    # insert a items to be scored
    self._initialize_environment_for_class_test()
    # instantiate class
    sc = SC(
      self._sc_config,
      self._sc_score_request_dict,
      self._sc_database, 
      self._sc_tf_collection,
      self._sc_idf_collection
    )
    # extract query terms
    await sc._extract_query_terms()
    # load weights
    await sc._load_weights()
    # check if we have the right terms and item in the weights dataframe
    assert sorted(sc._col2term) == sorted(self._sc_query_terms)
    #print(sc._row2item)
    #print(self._sc_items_ids)
    assert sorted(sc._row2item) == sorted(self._sc_items_ids)


  # compute scores
  @pytest.mark.asyncio
  async def test_compute_scores(self):
    print("test_score_computation.test_compute_scores")
    # insert a items to be scored
    self._initialize_environment_for_class_test()
    # instantiate class
    sc = SC(
      self._sc_config,
      self._sc_score_request_dict,
      self._sc_database, 
      self._sc_tf_collection,
      self._sc_idf_collection
    )
    # prepare for computing score
    await sc._extract_query_terms()
    await sc._load_weights()
    # compute scores
    await sc._compute_scores()
    #
    #print(sc._v_scores)
    # check that we have all the expected scores
    assert sc._v_scores.shape[0] == len(self._sc_items_ids)
    # check that we have the correct term ids
    assert sorted(sc._row2item) == sorted(self._sc_items_ids)
    # check the individual scores
    sc_v_scores = sc._v_scores
    for item in test_data.test_scores_computation:
      v = round(sc_v_scores[
        sc._item2row[
          (item['group'],item['itemId'])
        ],0],6)
      assert v == item['score']



  # runWorkflow
  @pytest.mark.asyncio
  async def test_run_workflow(self):
    print("test_scores_computation.test_run_workflow")
    # insert a items to be scored
    self._initialize_environment_for_class_test()
    # instantiate class
    sc = await SC.runWorkflow(
      self._sc_config,
      self._sc_score_request_dict,
      self._sc_database, 
      self._sc_tf_collection,
      self._sc_idf_collection
    )
    # query terms
    #print(sc)
    sc_query_terms = sc.getQueryTerms()
    # check that something was saved in the weights place holder
    assert sc_query_terms.sort() == self._sc_query_terms.sort()
    # scores length
    sc_scores_length = sc.getScoresLength()
    assert sc_scores_length == len(self._sc_items_ids)
    # scores
    sc_scores = {
      item['itemId'] : item['score']
      for item 
      in sc.getScores()
    }
    assert list(sc_scores.keys()).sort() == self._sc_items_ids.sort()
    for item in test_data.test_scores_computation:
      assert round(sc_scores[item['itemId']],6) == item['score']



