import datetime
import json

# database connection
test_database_uri = "mongodb://127.0.0.1:27017"
test_database = "pss_test"

file_test_data_items_plain = 'data/test/items_plain.json'
file_test_data_items_terms = 'data/test/items_with_terms.json'

# entries to use in testing the items endpoints
with open(file_test_data_items_plain,'r') as fh:
  test_items = json.load(fh)
with open(file_test_data_items_terms,'r') as fh:
  test_items_terms = json.load(fh)


#test_status_requested = datetime.datetime(2021, 9, 10, 8, 0, 36, 424175).isoformat()
#test_status_started = datetime.datetime(2021, 9, 10, 10, 1, 27, 593804).isoformat()
#test_status_ended = datetime.datetime(2021, 9, 10, 13, 26, 17, 91609).isoformat()
test_status_requested = datetime.datetime(2021, 9, 10, 8, 0, 36, 424000)
test_status_started = datetime.datetime(2021, 9, 10, 10, 1, 27, 593000)
test_status_ended = datetime.datetime(2021, 9, 10, 13, 26, 17, 91000)


test_status = {
  'not_run_yet' : {
    "id" :  "4D983232-8F13-4AD0-9933-51348379497D",
    "requested" : None,
    "started" : None,
    "ended" : None,
    "progressPercent" : 0.0,
    "progressDescription" : "",
    "inProgress" : False
  },
  'requested' : {
    "id" :  "C4B583B7-85C8-4C1E-83C3-1B23DBC3353C",
    "requested" : test_status_requested,
    "started" : None,
    "ended" : None,
    "progressPercent" : 0.0,
    "progressDescription" : "Fake requested",
    "inProgress" : True
  },
  'in_progress' : {
    "id" :  "60766773-7C68-4C89-BFE0-B14EE4233A32",
    "requested" : test_status_requested,
    "started" : test_status_started,
    "ended" : None,
    "progressPercent" : 0.4,
    "progressDescription" : "Fake weight computation",
    "inProgress" : True
  },
  'done' : {
    "id" :  "6D72FF4B-84BE-41DB-ABD4-736C711E0F93",
    "requested" : test_status_requested,
    "started" : test_status_started,
    "ended" : test_status_ended,
    "progressPercent" : 1.0,
    "progressDescription" : "Fake weight computation",
    "inProgress" : False
  }
}

test_weights_timestamp_1 = datetime.datetime(2021, 9, 10, 8, 0, 36, 42400).isoformat()
test_weights_timestamp_2 = datetime.datetime(2021, 9, 10, 10, 1, 27, 593000).isoformat()
test_weights_timestamp_3 = datetime.datetime(2021, 9, 10, 13, 26, 17, 91000).isoformat()

test_weights = {
  'weight_1_1' : {
    'id' : "3E144A19-496D-43CA-9FDD-4F2F56E7BF57",
    #'term' : 'information',
    'term' : 'inform',
    'itemId' : '24CC73BD-3A88-4AD7-B9B4-5C01AEC2456E',
    'itemGroup': "group_1",
    'timestamp' : test_weights_timestamp_1,
    'value' : 0.11
  },
  'weight_1_2' : {
    'id' : "1BFDBDAC-ECA6-44BB-AC0D-73D512978D9E",
    #'term' : 'information',
    'term' : 'inform',
    'itemId' : '37BBB678-4E40-43AC-998D-454E667AEDBF',
    'itemGroup': "group_1",
    'timestamp' : test_weights_timestamp_1,
    'value' : 0.12
  },
  'weight_1_3' : {
    'id' : "2234CD79-8CD9-4809-9354-81A70DCD7466",
    #'term' : 'information',
    'term' : 'inform',
    'itemId' : 'F2FC84A3-9A0A-48A9-87EF-07C752C8E5B4',
    'itemGroup': "group_1",
    'timestamp' : test_weights_timestamp_1,
    'value' : 0.13
  },
  'weight_1_4' : {
    'id' : "2260E18F-8CA8-4414-94A3-986A42B7E38C",
    #'term' : 'information',
    'term' : 'inform',
    'itemId' : '4D983232-8F13-4AD0-9933-51348379497D',
    'itemGroup': "default",
    'timestamp' : test_weights_timestamp_1,
    'value' : 0.14
  },
  'weight_1_5' : {
    'id' : "BB6DB517-9392-4500-BDC5-3B3C0314F607",
    #'term' : 'information',
    'term' : 'inform',
    'itemId' : 'A08C952D-4888-424F-B115-B5BCAC821B67',
    'itemGroup': "group_1",
    'timestamp' : test_weights_timestamp_1,
    'value' : 0.15
  },
  'weight_2_1' : {
    'id' : "4C75587E-B620-4930-88E6-E0F75E591E40",
    'term' : 'metadata',
    'itemId' : '37BBB678-4E40-43AC-998D-454E667AEDBF',
    'itemGroup': "group_1",
    'timestamp' : test_weights_timestamp_2,
    'value' : 0.21
  },
  'weight_2_2' : {
    'id' : "F2F4E7E0-A080-49C4-B481-F0F536BB8D59",
    'term' : 'metadata',
    'itemId' : '4D983232-8F13-4AD0-9933-51348379497D',
    'itemGroup': "default",
    'timestamp' : test_weights_timestamp_2,
    'value' : 0.22
  },
  'weight_3_1' : {
    'id' : "4F9319CB-C5D9-49B5-8707-57DFC445AF35",
    #'term' : 'retrieval',
    'term' : 'retriev',
    'itemId' : '24CC73BD-3A88-4AD7-B9B4-5C01AEC2456E',
    'itemGroup': "group_1",
    'timestamp' : test_weights_timestamp_3,
    'value' : 0.31
  },
  'weight_3_2' : {
    'id' : "F7019D62-CEC7-4CEC-8778-5D3DABD50649",
    #'term' : 'retrieval',
    'term' : 'retriev',
    'itemId' : '37BBB678-4E40-43AC-998D-454E667AEDBF',
    'itemGroup': "group_1",
    'timestamp' : test_weights_timestamp_3,
    'value' : 0.32
  },
}


test_scores_started = datetime.datetime(2021, 9, 10, 8, 0, 36, 424000)
test_scores_ended = datetime.datetime(2021, 9, 10, 10, 1, 27, 593000)

test_scores = {
  'data_1' : {
    'query' : 'test the scoring',
    'terms' : ['test', 'scor'],
    'itemIds' : [ 
      '7660171a-3421-461d-b2c7-1d9c575dcf1f',
      '3136f700-572e-4b5c-98ac-1b7bf21be75a',
      'f7bf042e-e249-48b5-8f03-27de390f20f8',
      '4e602cd8-eacd-447f-a087-1000021f55b0',
      '53fcf368-9b59-48f4-8a56-3166d4d89414',
      '03c97039-d2bc-4e02-b70e-0ae9e17b1821',
      '6f51db9c-56e1-4714-a2d2-ed1b5426ee95',
      '2178af78-1ece-4f40-9c3c-4e5e3eabe2a0',
      'ca6634ab-0dec-41d8-8a09-8a3f4db8b40b',
      '07a6cda2-d50a-4775-bcc1-b9517473c1c2'
    ],
    'scores' : [
      {
        'itemId' : '7660171a-3421-461d-b2c7-1d9c575dcf1f',
        'score' : 0.10,
        'group' : 'group_1'
      },
      {
        'itemId' : '3136f700-572e-4b5c-98ac-1b7bf21be75a',
        'score' : 0.12,
        'group' : 'group_2'
      },
      {
        'itemId' : 'f7bf042e-e249-48b5-8f03-27de390f20f8',
        'score' : 0.14,
        'group' : 'group_1'
      },
      {
        'itemId' : '4e602cd8-eacd-447f-a087-1000021f55b0',
        'score' : 0.16,
        'group' : 'group_2'
      },
      {
        'itemId' : '53fcf368-9b59-48f4-8a56-3166d4d89414',
        'score' : 0.18,
        'group' : 'group_1'
      },
      {
        'itemId' : '03c97039-d2bc-4e02-b70e-0ae9e17b1821',
        'score' : 0.20,
        'group' : 'group_2'
      },
      {
        'itemId' : '6f51db9c-56e1-4714-a2d2-ed1b5426ee95',
        'score' : 0.22,
        'group' : 'group_1'
      },
      {
        'itemId' : '2178af78-1ece-4f40-9c3c-4e5e3eabe2a0',
        'score' : 0.24,
        'group' : 'group_2'
      },
      {
        'itemId' : 'ca6634ab-0dec-41d8-8a09-8a3f4db8b40b',
        'score' : 0.26,
        'group' : 'group_1'
      },
      {
        'itemId' : '07a6cda2-d50a-4775-bcc1-b9517473c1c2',
        'score' : 0.28,
        'group' : 'group_2'
      }
    ],
    'computeInProgress' : False
  }
}

test_scores_computation = [
  {
    'itemId' : '37bbb678-4e40-43ac-998d-454e667aedbf',
    'score' : 0.910366
  },
  {
    'itemId' : '24cc73bd-3a88-4ad7-b9b4-5c01aec2456e',
    'score' : 0.902861
  },
  {
    'itemId' : '4d983232-8f13-4ad0-9933-51348379497d',
    'score' : 0.707107
  },
  {
    'itemId' : 'a08c952d-4888-424f-b115-b5bcac821b67',
    'score' : 0.707107
  }
]
