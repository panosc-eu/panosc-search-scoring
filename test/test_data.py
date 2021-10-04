import datetime

# database connection
test_database_uri = "mongodb://127.0.0.1:27017"
test_database = "pss_test"

# entries to use in testing the items endpoints
test_items = {
  "item_1" : {
    "id" : "24CC73BD-3A88-4AD7-B9B4-5C01AEC2456E",
    "group" : "group_1",
    "fields" : {
      "title" : "term frequency inverse document frequency",
      "description" : "In information retrieval, tf–idf, TF*IDF, or TFIDF, short for term frequency–inverse document frequency, is a numerical statistic that is intended to reflect how important a word is to a document in a collection or corpus.[1] It is often used as a weighting factor in searches of information retrieval, text mining, and user modeling. The tf–idf value increases proportionally to the number of times a word appears in the document and is offset by the number of documents in the corpus that contain the word, which helps to adjust for the fact that some words appear more frequently in general. tf–idf is one of the most popular term-weighting schemes today. A survey conducted in 2015 showed that 83% of text-based recommender systems in digital libraries use tf–idf. Variations of the tf–idf weighting scheme are often used by search engines as a central tool in scoring and ranking a document's relevance given a user query. tf–idf can be successfully used for stop-words filtering in various subject fields, including text summarization and classification. One of the simplest ranking functions is computed by summing the tf–idf for each query term; many more sophisticated ranking functions are variants of this simple model",
    }
  },
  "item_2" : {
    "id" : "37BBB678-4E40-43AC-998D-454E667AEDBF",
    "group" : "group_1",
    "fields" : {
      "title" : "Information retrieval",
      "description" : "Information retrieval (IR) is the process of obtaining information system resources that are relevant to an information need from a collection of those resources. Searches can be based on full-text or other content-based indexing. Information retrieval is the science of searching for information in a document, searching for documents themselves, and also searching for the metadata that describes data, and for databases of texts, images or sounds. Automated information retrieval systems are used to reduce what has been called information overload. An IR system is a software system that provides access to books, journals and other documents; stores and manages those documents. Web search engines are the most visible IR applications.",
    }
  },
  "item_3" : {
    "id" : "F2FC84A3-9A0A-48A9-87EF-07C752C8E5B4",
    "group" : "group_1",
    "fields" : {
      "title" : "Information system",
      "description" : "An information system (IS) is a formal, sociotechnical, organizational system designed to collect, process, store, and distribute information.[1] From a sociotechnical perspective, information systems are composed by four components: task, people, structure (or roles), and technology.[2] Information systems can be defined as an integration of components for collection, storage and processing of data of which the data is used to provide information, contribute to knowledge as well as digital products that facilitate decision making.[3] A computer information system is a system composed of people and computers that processes or interprets information.[4][5][6][7] The term is also sometimes used to simply refer to a computer system with software installed. Information Systems is an academic study of systems with a specific reference to information and the complementary networks of hardware and software that people and organizations use to collect, filter, process, create and also distribute data. An emphasis is placed on an information system having a definitive boundary, users, processors, storage, inputs, outputs and the aforementioned communication networks.[8]",
    }
  },
  "item_4" : {
    "id" : "4D983232-8F13-4AD0-9933-51348379497D",
    "fields" : {
      "title" : "Metadata",
      "description" : "Metadata is \"data that provides information about other data\".[1] In other words, it is \"data about data\". Many distinct types of metadata exist, including descriptive metadata, structural metadata, administrative metadata,[2] reference metadata, statistical metadata[3] and legal metadata. Descriptive metadata is descriptive information about a resource. It is used for discovery and identification. It includes elements such as title, abstract, author, and keywords. Structural metadata is metadata about containers of data and indicates how compound objects are put together, for example, how pages are ordered to form chapters. It describes the types, versions, relationships and other characteristics of digital materials.[4] Administrative metadata is information to help manage a resource, like resource type, permissions, and when and how it was created.[5] Reference metadata is information about the contents and quality of statistical data. Statistical metadata, also called process data, may describe processes that collect, process, or produce statistical data.[6] Legal metadata provides information about the creator, copyright holder, and public licensing, if provided. This is not an exhaustive list and metadata is not strictly bounded to one of these categories, as it can be used to describe a piece of data in many other ways."
    }
  },
  "item_5" : {
    "id" : "A08C952D-4888-424F-B115-B5BCAC821B67",
    "group" : "group_1",
    "fields" : {
      "title" : "Information overload",
      "description" : "Information overload (also known as infobesity,[1][2] infoxication,[3] information anxiety,[4] and information explosion[5]) is the difficulty in understanding an issue and effectively making decisions when one has too much information (TMI) about that issue,[6] and is generally associated with the excessive quantity of daily information. The term \"Information overload\" was first used in Bertram Gross' 1964 book, The Managing of Organizations,[7] and was further popularized by Alvin Toffler in his bestselling 1970 book Future Shock.[8] Speier et al. (1999) said that if input exceeds the processing capacity, information overload occurs, which is likely to reduce the quality of the decisions.[9] In a newer definition, Roetzel (2019) focuses on time and resources aspects. He states that when a decision-maker is given many sets of information, such as complexity, amount, and contradiction, the quality of its decision is decreased because of the individual’s limitation of scarce resources to process all the information and optimally make the best decision.[10] The advent of modern information technology has been a primary driver of information overload on multiple fronts: in quantity produced, ease of dissemination, and breadth of the audience reached. Longstanding technological factors have been further intensified by the rise of social media and the attention economy, which facilitates attention theft.[11][12] In the age of connective digital technologies, informatics, the Internet culture (or the digital culture), information overload is associated with over-exposure, excessive viewing of information, and input abundance of information and data.",
    }    
  },
  "item_6" : {
    "id" : "68BA942F-A5BC-422D-8B91-4DE07441A312",
    "fields" : {
      "title" : "Data",
      "description" : "Data are individual facts, statistics, or items of information, often numeric, that are collected through observation. In a more technical sense, data are a set of values of qualitative or quantitative variables about one or more persons or objects, while a datum (singular of data) is a single value of a single variable. Although the terms \"data\" and \"information\" are often used interchangeably, these terms have distinct meanings. In some popular publications, data are sometimes said to be transformed into information when they are viewed in context or in post-analysis. However, in academic treatments of the subject data are simply units of information. Data are used in scientific research, businesses management (e.g., sales data, revenue, profits, stock price), finance, governance (e.g., crime rates, unemployment rates, literacy rates), and in virtually every other form of human organizational activity (e.g., censuses of the number of homeless people by non-profit organizations)"
    }
  },
}

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
    'timestamp' : test_weights_timestamp_1,
    'value' : 0.11
  },
  'weight_1_2' : {
    'id' : "1BFDBDAC-ECA6-44BB-AC0D-73D512978D9E",
    #'term' : 'information',
    'term' : 'inform',
    'itemId' : '37BBB678-4E40-43AC-998D-454E667AEDBF',
    'timestamp' : test_weights_timestamp_1,
    'value' : 0.12
  },
  'weight_1_3' : {
    'id' : "2234CD79-8CD9-4809-9354-81A70DCD7466",
    #'term' : 'information',
    'term' : 'inform',
    'itemId' : 'F2FC84A3-9A0A-48A9-87EF-07C752C8E5B4',
    'timestamp' : test_weights_timestamp_1,
    'value' : 0.13
  },
  'weight_1_4' : {
    'id' : "2260E18F-8CA8-4414-94A3-986A42B7E38C",
    #'term' : 'information',
    'term' : 'inform',
    'itemId' : '4D983232-8F13-4AD0-9933-51348379497D',
    'timestamp' : test_weights_timestamp_1,
    'value' : 0.14
  },
  'weight_1_5' : {
    'id' : "BB6DB517-9392-4500-BDC5-3B3C0314F607",
    #'term' : 'information',
    'term' : 'inform',
    'itemId' : 'A08C952D-4888-424F-B115-B5BCAC821B67',
    'timestamp' : test_weights_timestamp_1,
    'value' : 0.15
  },
  'weight_2_1' : {
    'id' : "4C75587E-B620-4930-88E6-E0F75E591E40",
    'term' : 'metadata',
    'itemId' : '37BBB678-4E40-43AC-998D-454E667AEDBF',
    'timestamp' : test_weights_timestamp_2,
    'value' : 0.21
  },
  'weight_2_2' : {
    'id' : "F2F4E7E0-A080-49C4-B481-F0F536BB8D59",
    'term' : 'metadata',
    'itemId' : '4D983232-8F13-4AD0-9933-51348379497D',
    'timestamp' : test_weights_timestamp_2,
    'value' : 0.22
  },
  'weight_3_1' : {
    'id' : "4F9319CB-C5D9-49B5-8707-57DFC445AF35",
    #'term' : 'retrieval',
    'term' : 'retriev',
    'itemId' : '24CC73BD-3A88-4AD7-B9B4-5C01AEC2456E',
    'timestamp' : test_weights_timestamp_3,
    'value' : 0.31
  },
  'weight_3_2' : {
    'id' : "F7019D62-CEC7-4CEC-8778-5D3DABD50649",
    #'term' : 'retrieval',
    'term' : 'retriev',
    'itemId' : '37BBB678-4E40-43AC-998D-454E667AEDBF',
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
        'id' : '7660171a-3421-461d-b2c7-1d9c575dcf1f',
        'score' : 0.10,
        'group' : 'group_1'
      },
      {
        'id' : '3136f700-572e-4b5c-98ac-1b7bf21be75a',
        'score' : 0.12,
        'group' : 'group_2'
      },
      {
        'id' : 'f7bf042e-e249-48b5-8f03-27de390f20f8',
        'score' : 0.14,
        'group' : 'group_1'
      },
      {
        'id' : '4e602cd8-eacd-447f-a087-1000021f55b0',
        'score' : 0.16,
        'group' : 'group_2'
      },
      {
        'id' : '53fcf368-9b59-48f4-8a56-3166d4d89414',
        'score' : 0.18,
        'group' : 'group_1'
      },
      {
        'id' : '03c97039-d2bc-4e02-b70e-0ae9e17b1821',
        'score' : 0.20,
        'group' : 'group_2'
      },
      {
        'id' : '6f51db9c-56e1-4714-a2d2-ed1b5426ee95',
        'score' : 0.22,
        'group' : 'group_1'
      },
      {
        'id' : '2178af78-1ece-4f40-9c3c-4e5e3eabe2a0',
        'score' : 0.24,
        'group' : 'group_2'
      },
      {
        'id' : 'ca6634ab-0dec-41d8-8a09-8a3f4db8b40b',
        'score' : 0.26,
        'group' : 'group_1'
      },
      {
        'id' : '07a6cda2-d50a-4775-bcc1-b9517473c1c2',
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
