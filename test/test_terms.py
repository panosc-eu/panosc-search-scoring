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
from app.routers import terms as termsRouter
from test.pss_test_base import pss_test_base
from app.models.terms import TermResponseModel


class TestTerms(pss_test_base):

  # define test database
  _db_database_uri = test_data.test_database_uri
  _db_database_name = test_data.test_database
  _db_collection_name = weightsRouter.endpointRoute
  # define collection we want to work with
  _endpoint_name = termsRouter.endpointRoute
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
      self._db_collection = self._db_database[itemsRouter.endpointRoute]
      self._data = test_data.test_items
      res = super()._populateDatabase()

      # than inserts weights
      self._db_collection = self._db_database[weightsRouter.endpointRoute]
      self._data = test_data.test_weights
      return super()._populateDatabase()


  def _countGroupAndItems(self,group=None):
    # items to group
    itemVsGroup = {
      item['id'].lower(): item['group'] if 'group' in item.keys() else 'default' 
      for item 
      in test_data.test_items.values()
    }

    # list items and groups for each term
    dTerms = {}
    for term in test_data.test_weights.values():
      termName = term['term'].lower()
      itemId = term['itemId'].lower()
      itemGroup = itemVsGroup[itemId] 
      if group is not None and itemGroup != group:
        # not in the selected group, skip it
        continue

      if termName not in dTerms.keys():
        dTerms[termName] = {
          'term' : termName,
          'itemIds' : set(itemId),
          'itemGroups' : set(itemGroup) 
        }
      else:
        dTerms[termName]['itemIds'].add(itemId)
        dTerms[termName]['itemGroups'].add(itemGroup)

    # count items and groups
    termCounts = [
      {
        'term' : term['term'],
        'numberOfItems' : len(term['itemIds']),
        'numberOfGroups' : len(term['itemGroups'])
      }
      for term
      in dTerms.values()
    ]
    return termCounts

  # 
  # TESTS
  # ================

  # get all terms
  def test_get_terms(self):
    print("test_compute.test_get_terms")
    # insert test weights
    test_weights = self._populateDatabase()
    term_counts = self._countGroupAndItems()
    #
    with TestClient(app.app) as client:
      # request status
      response = client.get(
        self._endpoint_url
      )
      assert response.status_code == 200
      jsonResponse = response.json()
      print(jsonResponse)
      jsonResponse = [TermResponseModel(**item) for item in response.json()]
      assert len(jsonResponse) == len(term_counts)


  # get terms from group
  def test_get_group_terms(self):
    print("test_compute.test_get_group_terms")
    # insert test terms
    test_weights = self._populateDatabase()
    term_counts = self._countGroupAndItems(self._selectedGroup)
    # count item in group 1
    with TestClient(app.app) as client:
      # request status
      response = client.get(
        self._endpoint_url + '?group=' + self._selectedGroup
      )
      
      assert response.status_code == 200
      jsonResponse = [TermResponseModel(**item) for item in response.json()]
      assert len(jsonResponse) == len(term_counts)


  # count terms
  def test_count_all_terms(self):
    print("test_compute.test_count_all_terms")
    # insert test terms
    test_weights = self._populateDatabase()
    term_counts = self._countGroupAndItems()
    # count all items
    with TestClient(app.app) as client:
      # request status
      response = client.get(
        self._endpoint_url + '/count',
      )
      
      print(response)
      assert response.status_code == 200
      jsonResponse = response.json()
      assert jsonResponse["count"] == len(term_counts)


  # count terms in group 1
  def test_count_group_terms(self):
    print("test_compute.test_count_group_weights")
    # insert test weigths
    test_weights = self._populateDatabase()
    term_counts = self._countGroupAndItems(self._selectedGroup)
    # count item in group 1
    with TestClient(app.app) as client:
      # request status
      response = client.get(
        self._endpoint_url + '/count?group=' + self._selectedGroup,
      )
      
      assert response.status_code == 200
      jsonResponse = response.json()
      assert jsonResponse["count"] == len(term_counts)

  # count terms in empty dataset
  def test_count_group_terms(self):
    print("test_compute.test_count_weights_in_empty_database")
    # count terms
    with TestClient(app.app) as client:
      # request status
      response = client.get(
        self._endpoint_url + '/count'
      )
      
      assert response.status_code == 200
      jsonResponse = response.json()
      assert jsonResponse["count"] == 0

