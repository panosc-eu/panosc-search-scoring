# testing suite for Panosc Search Scoring
# all weights endpoints
#  

from json.decoder import JSONDecodeError
from fastapi.testclient import TestClient
#from mock.mock import AsyncMock
import pymongo
import datetime
import pytest
from copy import deepcopy
from collections import Counter
from mock import AsyncMock, Mock, patch, PropertyMock

from app import app
import test.test_data as test_data
from app.routers import weights as weightsRouter
#from app.routers import items as itemsRouter
from app.routers import score as scoreRouter
from app.routers import compute as computeRouter
from test.pss_test_base import pss_test_base
from app.models.terms import TermResponseModel


class TestTerms(pss_test_base):

  # define test database
  _db_database_uri = test_data.test_database_uri
  _db_database_name = test_data.test_database
  _db_collection_name = computeRouter.endpointRoute
  # define collection we want to work with
  _endpoint_name = scoreRouter.endpointRoute
  _data = [test_data.test_status['done']]
  _score_data = test_data.test_scores['data_1']
  # group selected for testing with group
  _selectedGroup = 'group_1'

  #
  # TESTS
  # =================
  #@pytest.mock.asyncio
  @patch("app.routers.score.SC",new_callable=AsyncMock)
  def test_post_score(self,mock_SC):
    print("test_score.test_post_score")

    query = self._score_data['query']
    terms = self._score_data['terms']
    scores = self._score_data['scores']

    #
    with TestClient(app.app) as client:
      # mocks the call to the score compute class
      SC = Mock()
      #SC.runWorkflow.return_value = None
      SC.getQueryTerms.return_value = terms
      SC.getScores.return_value = scores
      SC.getScoresLength.return_value = len(scores)
      type(SC).started = PropertyMock(return_value='started')
      type(SC).ended = PropertyMock(return_value='ended')
      
      #mock_sc = mock_SC.return_value
      mock_SC.runWorkflow.return_value = SC

      request = {
        'query' : query,
        'itemIds' : self._score_data['itemIds']
      }

      response = client.post(
        url=self._endpoint_url,
        json=request
      )

      assert response.status_code == 200
      jsonResponse = response.json()
      assert jsonResponse['request']['query'] == request['query']
      assert jsonResponse['request']['itemIds'] == request['itemIds']
      assert jsonResponse['query']['query'] == query
      assert jsonResponse['query']['terms'] == terms
      assert jsonResponse['scores'] == scores
      assert jsonResponse['dimension'] == len(scores)
      assert jsonResponse['computeInProgress'] == False
      assert jsonResponse['started'] == 'started'
      assert jsonResponse['ended'] == 'ended'

