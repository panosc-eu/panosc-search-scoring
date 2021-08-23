from fastapi.testclient import TestClient
from starlette.requests import ClientDisconnect
from ..app import app

client = TestClient(app)

def test_root():
  response = client.get('/')
  assert response.status_code == 200
  responseDict = response.json()
  responseFields = list(responseDict.keys())
  assert 'application' in responseFields
  assert 'description' in responseFields
  assert 'version' in responseFields
  assert 'startedtime' in responseFields
  assert 'currenttime' in responseFields
  assert 'uptime' in responseFields
  