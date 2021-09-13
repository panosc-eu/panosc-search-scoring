# testing suite for Panosc Search Scoring
# all items endpoints
#  

from json.decoder import JSONDecodeError
from fastapi.testclient import TestClient
import pymongo
import datetime
import pytest
from copy import deepcopy

from app import app
import test.test_data as test_data
from app.routers import items as itemsRouter


#
# not sure which implementation I should use
#@pytest.fixture(autouse=True)
#def run_around_tests():
#  # set up environment
#  # empty database
#
#  yield
#
#  # tear down environment
#  # empty database
#

# or

#def setup_module(module):

test_items_db_client = None
test_items_db_database = None

#
# support functions
# --------------------------
# empty the database
def empty_database():
  global test_items_db_client
  global test_items_db_database

  if test_items_db_client is None:
    # connect to database
    test_items_db_client = pymongo.MongoClient(test_data.test_database_uri)
    test_items_db_database = test_items_db_client[test_data.test_database]
    
  print(test_items_db_database)
  print(test_items_db_database.list_collection_names())

  # delete all the collections
  for coll_name in test_items_db_database.list_collection_names():
    print("Dropping collection : " + coll_name)
    temp_coll = test_items_db_database[coll_name]
    temp_coll.drop()


# lowercase uuid
def lowercaseItemId(item):
  item['id'] = item['id'].lower()
  return item

# prepare item to be inserted in database
def prepItemForInsertion(inItem):
  outItem = deepcopy(inItem)
  outItem['_id'] = outItem['id'].lower()
  del outItem['id']
  return outItem


# create items in database
def populateDatabase(numberOfItems=-1):
  # items to be created
  items_to_be_created = [
    lowercaseItemId(dict(item)) 
    for item 
    in test_data.test_items.values()
  ]
  if numberOfItems>0:
    items_to_be_created = items_to_be_created[0:numberOfItems]

  # retrieve the database collection
  test_items_db_collection = test_items_db_database[itemsRouter.endpointRoute]
  
  # insert items in collection
  res = test_items_db_collection.insert_many(
    [prepItemForInsertion(item) for item in items_to_be_created]
  )

  return items_to_be_created


def setup_function(function):
  # clear database
  empty_database()


def teardown_module(module):
  # clear database
  empty_database()


# 
# TESTS
# ================

# create single item
def test_create_single_item():
  # item to be used
  item_to_be_created = list(test_data.test_items.values())[0]
  
  with TestClient(app.app) as client:
    # successful creation
    response = client.post(
      url="/items/",
      json=item_to_be_created
    )
    assert response.status_code == 201
    jsonResponse = response.json()
    assert jsonResponse["success"] == True
    assert jsonResponse["items_created"] == 1
    assert jsonResponse["items_ids"] == [item_to_be_created["id"].lower()]


# tries to create an item with duplicated id
def test_create_single_item_with_duplicated_id():
  # item to be used
  item_to_be_created = list(test_data.test_items.values())[0]
  
  with TestClient(app.app) as client:
    # creation first instance of item
    response = client.post(
      url='/items/',
      json=item_to_be_created
    )
    assert response.status_code == 201
    # failed creation
    try:
      response = client.post(
        url='/items/',
        json=item_to_be_created
      )
      assert False
    except:
      assert True


# tries to create an item with missing id
def test_create_single_item_with_missing_id():
  # item to be used
  item_to_be_created = dict(list(test_data.test_items.values())[0])
  del item_to_be_created["id"]

  with TestClient(app.app) as client:
    # failed creation
    try:
      response = client.post(
        url='/items/',
        json=item_to_be_created
      )
      assert False
    except:
      assert True



# create multiple items
def test_create_multiple_items():
  # list of items to be created
  items_to_be_created = list(test_data.test_items.values())
  items_ids = [item["id"].lower() for item in items_to_be_created]

  with TestClient(app.app) as client:
    # successful creation
    response = client.post(
      url="/items/",
      json=items_to_be_created
    )
    assert response.status_code == 201
    jsonResponse = response.json()
    assert jsonResponse["success"] == True
    assert jsonResponse["items_created"] == len(items_to_be_created)
    assert jsonResponse["items_ids"] == items_ids


# tries to create an item with duplicated id
def test_create_multiple_items_with_duplicated_id():
  # list of items to be created
  items_to_be_created = deepcopy(list(test_data.test_items.values()))
  items_to_be_created.append(items_to_be_created[0])
  
  with TestClient(app.app) as client:
    try:
      # failed creation
      response = client.post(
        url='/items/',
        json=items_to_be_created
      )
      assert False
    except:
      assert True


# tries to create mutiple items where one is missing the id
def test_create_multiple_items_with_missing_id():
  # list of items to be created
  items_to_be_created = deepcopy(list(test_data.test_items.values()))
  item_without_id = deepcopy(items_to_be_created[0])
  del item_without_id["id"]
  items_to_be_created.append(item_without_id)

  with TestClient(app.app) as client:
    try:
      # failed creation
      response = client.post(
        url='/items',
        json=items_to_be_created
      )
      assert False
    except:
      assert True


# count items
def test_count_items():
  test_items = populateDatabase()
  
  with TestClient(app.app) as client:
    # count items
    response = client.get(
      url='/items/count'
    )
    assert response.status_code == 200
    jsonResponse = response.json()
    assert jsonResponse['count'] == len(test_items)


# retrieve all items
def test_get_all_items():
  test_items = populateDatabase()

  with TestClient(app.app) as client:
    # plain call
    response = client.get(
      '/items/'
    )
    assert response.status_code == 200
    jsonResponse = response.json()
    # checks that the number of items returned matches the number of items inserted
    assert len(jsonResponse) == len(test_items)
    # checks that the ids of the items returned are the same as the ids of the item inserted
    assert len(
      list(
        set([item['id'] for item in jsonResponse]).difference(
          set([item['id'] for item in test_items])
        )
      )
    ) == 0

    # call using limit
    response = client.get(
      '/items/?limit=2'
    )
    assert response.status_code == 200
    jsonResponse = response.json()
    # checks that the number of items returned are exactly 2
    assert len(jsonResponse) == 2
  
    # call using offset
    response = client.get(
      '/items/?offset=1'
    )
    assert response.status_code == 200
    jsonResponse = response.json()
    # checks that the number of items returned are exactly the number of items inserted minus 1
    assert len(jsonResponse) == (len(test_items) - 1)
  
    # call using limit and offset
    response = client.get(
      '/items/?limit=1&offset=0'
    )
    assert response.status_code == 200
    jsonResponse1 = response.json()
    # checks that the number of items returned are exactly 1
    assert len(jsonResponse1) == 1
    # place second call
    response = client.get(
      '/items/?limit=1&offset=3'
    )
    assert response.status_code == 200
    jsonResponse2 = response.json()
    # checks that the number of items returned are exactly 1
    assert len(jsonResponse2) == 1
    # checks that the 2 elements returned are different
    assert jsonResponse1[0]['id'] != jsonResponse2[0]['id']

  
# retrieve one item
def test_get_single_existing_item():
  test_items = populateDatabase()

  with TestClient(app.app) as client:
    # test with the first 2 items of test data
    for item in test_items[0:2]:
      # call using limit and offset
      response = client.get(
        '/items/' + item['id']
      )
      assert response.status_code == 200
      jsonResponse = response.json()
      assert jsonResponse['id'] == item['id']


# retrieve item not existing
def test_get_single_non_existing_item():
  test_items = populateDatabase()

  with TestClient(app.app) as client:
    # create an invalid uuid
    fake_item_id = '-'.join(test_items[0]['id'].split('-')[0:-2])+'-invalididher'

    # call using limit and offset
    response = client.get(
      '/items/' + fake_item_id
    )
    assert response.status_code == 404
    jsonResponse = response.json()
    print(jsonResponse)
    assert jsonResponse is None


# update item with put
def test_put_update_item():
  originalItem = populateDatabase(1)[0]

  with TestClient(app.app) as client:
    # changes group and fields
    modifiedItem1 = {
      "group" : "group_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"),
      "fields" : {
        "field_1" : "value_1_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
      }
    }
    # calls the api with the full object
    print(originalItem)
    print(modifiedItem1)
    response = client.put(
      url="/items/" + originalItem["id"],
      json=modifiedItem1
    )
    assert response.status_code == 200
    jsonResponse = response.json()
    assert jsonResponse['successful'] == True
    assert jsonResponse["items_updated"] == 1
    # retrieve object
    response = client.get(
      url="/items/" + originalItem['id']
    )
    assert response.status_code == 200
    jsonResponse = response.json()
    assert jsonResponse['group'] == modifiedItem1['group']
    assert jsonResponse['fields'] == modifiedItem1['fields']

    # now update with partial object
    # changes group and fields
    modifiedItem2 = {
      "fields" : {
        "field_1" : "value_1_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
      }
    }
    try:
      # calls the api with the partial object
      response = client.put(
        url="/items/" + originalItem["id"],
        json=modifiedItem2
      )
      assert False
    except:
      assert True


# update item with patch
def test_patch_update_item():
  originalItem = populateDatabase(1)[0]

  with TestClient(app.app) as client:
    # changes group and fields
    modifiedFields = {
      "fields" : {
        "field_1" : "value_1_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
      }
    }
    # calls the api with the full object
    response = client.patch(
      url="/items/" + originalItem["id"],
      json=modifiedFields
    )
    assert response.status_code == 200
    jsonResponse = response.json()
    assert jsonResponse['successful'] == True
    assert jsonResponse["items_updated"] == 1
    # retrieve object
    response = client.get(
      url="/items/" + originalItem['id']
    )
    assert response.status_code == 200
    jsonResponse = response.json()
    assert jsonResponse['group'] == originalItem['group']
    assert jsonResponse['fields'] == modifiedFields['fields']


# delete item
def test_delete_item():
  item = populateDatabase(1)[0]

  with TestClient(app.app) as client:
    # delete item
    response = client.delete(
      url="/items/" + item['id']
    )
    assert response.status_code == 200
    jsonResponse = response.json()
    assert jsonResponse['successful'] == True
    assert jsonResponse["items_deleted"] == 1
    # tries to retrieve the item
    response = client.get(
      url="/items/" + item['id']
    )
    assert response.status_code == 404
    jsonResponse = response.json()
    assert jsonResponse is None




