# testing suite for Panosc Search Scoring
# all weights endpoints
#  

from json.decoder import JSONDecodeError
from fastapi.testclient import TestClient
import pymongo
import datetime
import pytest
from copy import deepcopy
from collections import Counter

from app import app
import test.test_data as test_data
from app.routers import weights as weightsRouter
from app.routers import items as itemsRouter
from test.pss_test_base import pss_test_base
from app.models.weights import WeightResponseModel

from app.common.database import COLLECTION_ITEMS, COLLECTION_TF, COLLECTION_IDF


class TestWeights(pss_test_base):

  # define test database
  _db_database_uri = test_data.test_database_uri
  _db_database_name = test_data.test_database
  # define collection we want to work with
  _endpoint_name = weightsRouter.endpointRoute
  _data = ""
  # group selected for testing with group
  _selectedGroup = 'group_1'


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
      # first inserts items
      self._db_collection = self._db_database[COLLECTION_ITEMS]
      self._data = test_data.test_items
      res1 = super()._populateDatabase()

      # than inserts TF weights
      self._db_collection = self._db_database[COLLECTION_TF]
      self._data = test_data.test_weights_tf
      res2 = super()._populateDatabase()

      # than inserts IDF weights
      self._db_collection = self._db_database[COLLECTION_IDF]
      self._data = test_data.test_weights_idf
      res3 = super()._populateDatabase()

      return {
        'items' : res1,
        'tf' : res2,
        'idf' : res3
      }


  def _countGroupWeights(self):
    itemsVsGroups = {
      item['id'].lower(): item['group'] if 'group' in item.keys() else 'default' 
      for item 
      in test_data.test_items.values()
    }
    groups = [
      itemsVsGroups[item['itemId'].lower()] 
      for item 
      in test_data.test_weights_tf.values()
    ]
    return dict(Counter(groups))

  # 
  # TESTS
  # ================

  # get all weights
  def test_get_weights(self):
    print("test_compute.test_get_weights")
    # insert test weigths
    res = self._populateDatabase()
    test_weights = res['tf']
    #
    with TestClient(app.app) as client:
      # request status
      response = client.get(
        self._endpoint_url
      )
      assert response.status_code == 200
      jsonResponse = response.json()
      print(jsonResponse)
      #jsonResponse = [WeightResponseModel(**item) for item in response.json()]
      assert len(jsonResponse) == len(test_weights)


  # get weights from group
  def test_get_group_weights(self):
    print("test_compute.test_get_group_weights")
    # insert test weigths
    test_weights = self._populateDatabase()
    group_counts = self._countGroupWeights()
    # count item in group 1
    with TestClient(app.app) as client:
      # request status
      response = client.get(
        self._endpoint_url + '?group=' + self._selectedGroup,

      )
      
      assert response.status_code == 200
      jsonResponse = [WeightResponseModel(**item) for item in response.json()]
      assert len(jsonResponse) == group_counts[self._selectedGroup]


  # count weights
  def test_count_all_weights(self):
    print("test_compute.test_count_all_weights")
    # insert test weigths
    res = self._populateDatabase()
    test_weights = res['tf']
    # count all items
    with TestClient(app.app) as client:
      # request status
      response = client.get(
        self._endpoint_url + '/count',
      )
      
      print(response)
      assert response.status_code == 200
      jsonResponse = response.json()
      assert jsonResponse["count"] == len(test_weights)


  # count weights in group 1
  def test_count_group_weights(self):
    print("test_compute.test_count_group_weights")
    # insert test weigths
    test_weights = self._populateDatabase()
    group_counts = self._countGroupWeights()
    # count item in group 1
    with TestClient(app.app) as client:
      # request status
      response = client.get(
        self._endpoint_url + '/count?group=' + self._selectedGroup,
      )
      
      assert response.status_code == 200
      jsonResponse = response.json()
      assert jsonResponse["count"] == group_counts[self._selectedGroup]

