# testing suite for Panosc Search Scoring
# endpoints: compute
# notes: it does not actually compute the weights. 
#        For the weight compute testing check test_weight_computation
#  

from json.decoder import JSONDecodeError
from fastapi.testclient import TestClient
import pymongo
import datetime
import pytest
from copy import deepcopy
from mock import AsyncMock, Mock, patch

from app import app
import test.test_data as test_data
from app.routers import compute as computeRouter
from test.pss_test_base import pss_test_base
from app.models.compute import ComputeStatusResponseModel


class TestCompute(pss_test_base):

  # define test database
  _db_database_uri = test_data.test_database_uri
  _db_database_name = test_data.test_database
  # define collection we want to work with
  _endpoint_name = computeRouter.endpointRoute
  _data = test_data.test_status


  # auxiliary functions
  def _cleanTestData(self,inData):
    outData = deepcopy(inData[0])
    del outData['id']
    return outData


  # 
  # TESTS
  # ================

  # get, no status
  def test_get_no_status(self):
    print("test_compute.test_get_no_status")
    # database is empty = no status
    with TestClient(app.app) as client:
      # request status
      response = client.get(
        self._endpoint_url
      )
      
      assert response.status_code == 200
      jsonResponse = ComputeStatusResponseModel(**response.json())
      assert jsonResponse.progressPercent == 0
      assert jsonResponse.progressDescription == "Weights computation not yet run"
      assert jsonResponse.inProgress == False


  # get, not run yet
  def test_get_not_run_yet(self):
    # insert a status
    test_data = self._populateDatabase(itemKey='not_run_yet')
    test_data = self._cleanTestData(test_data)
    # database is empty = no status
    with TestClient(app.app) as client:
      # request status
      response = client.get(
        self._endpoint_url
      )

      assert response.status_code == 200
      jsonResponse = ComputeStatusResponseModel(**response.json()).dict()
      assert jsonResponse == test_data


# get, requested
  def test_get_requested(self):
    # insert a status
    test_data = self._populateDatabase(itemKey='requested')
    test_data = self._cleanTestData(test_data)
    # database is empty = no status
    with TestClient(app.app) as client:
      # request status
      response = client.get(
        self._endpoint_url
      )

      assert response.status_code == 200
      jsonResponse = ComputeStatusResponseModel(**response.json()).dict()
      assert jsonResponse == test_data


  # get, in progress
  def test_get_in_progress(self):
    # insert a status
    test_data = self._populateDatabase(itemKey='in_progress')
    test_data = self._cleanTestData(test_data)
    # database is empty = no status
    with TestClient(app.app) as client:
      # request status
      response = client.get(
        self._endpoint_url
      )

      assert response.status_code == 200
      jsonResponse = ComputeStatusResponseModel(**response.json()).dict()
      assert jsonResponse == test_data


  # get, compute done
  def test_get_compute_done(self):
    # insert a status
    test_data = self._populateDatabase(itemKey='done')
    test_data = self._cleanTestData(test_data)
    # database is empty = no status
    with TestClient(app.app) as client:
      # request status
      response = client.get(
        self._endpoint_url
      )

      assert response.status_code == 200
      jsonResponse = ComputeStatusResponseModel(**response.json()).dict()
      assert jsonResponse == test_data


  # get, multi status
  def test_get_multi_status(self):
    # insert all status
    test_data = self._populateDatabase()
    # database is empty = no status
    with TestClient(app.app) as client:
      # request status
      try:
        response = client.get(
          self._endpoint_url
        )
        assert False
      except:
        assert True


  # post multi status
  @patch("app.routers.compute.WC",new_callable=AsyncMock)
  def test_post_multi_status(self,mock_WC):
    # insert all status
    test_data = self._populateDatabase()
    # database has multiple status in db
    with TestClient(app.app) as client:
      # mocks the call to the score compute class
      WC = Mock()
      mock_WC.runWorkflow.return_value = WC

      # request status
      try:
        response = client.post(
          self._endpoint_url
        )
        assert False
      except:
        assert True
    

  # post no status
  @patch("app.routers.compute.WC",new_callable=AsyncMock)
  def test_post_no_status(self,mock_WC):
    # database is empty = no status
    with TestClient(app.app) as client:
      # mocks the call to the score compute class
      WC = Mock()
      mock_WC.runWorkflow.return_value = WC

      # request status
      response = client.post(
        self._endpoint_url
      )

      assert response.status_code == 200
      jsonResponse = ComputeStatusResponseModel(**response.json())
      assert jsonResponse.requested is not None
      assert jsonResponse.started is None
      assert jsonResponse.ended is None
      assert jsonResponse.progressDescription == ""
      assert jsonResponse.progressPercent == 0
      assert jsonResponse.inProgress == True


  # post one status done
  @patch("app.routers.compute.WC",new_callable=AsyncMock)
  def test_post_status_done(self, mock_WC):
    # insert a status
    test_data = self._populateDatabase(itemKey='done')
    # database is empty = no status
    with TestClient(app.app) as client:
      # mocks the call to the score compute class
      WC = Mock()
      mock_WC.runWorkflow.return_value = WC

      # request status
      response = client.post(
        self._endpoint_url
      )

      assert response.status_code == 200
      jsonResponse = ComputeStatusResponseModel(**response.json())
      assert jsonResponse.requested is not None
      assert jsonResponse.started is None
      assert jsonResponse.ended is None
      assert jsonResponse.progressDescription == ""
      assert jsonResponse.progressPercent == 0
      assert jsonResponse.inProgress == True


  # post one status in progress
  @patch("app.routers.compute.WC",new_callable=AsyncMock)
  def test_post_in_progress(self,mock_WC):
    # insert a status
    test_data = self._populateDatabase(itemKey='in_progress')
    test_data = self._cleanTestData(test_data)
    # database is empty = no status
    with TestClient(app.app) as client:
      # mocks the call to the score compute class
      WC = Mock()
      mock_WC.runWorkflow.return_value = WC

      # request status
      response = client.post(
        self._endpoint_url
      )

      assert response.status_code == 409
      jsonResponse = ComputeStatusResponseModel(**response.json()).dict()
      assert jsonResponse == test_data


