import datetime

# database connection
test_database_uri = "mongodb://127.0.0.1:27017"
test_database = "pss_test"

# entries to use in testing the items endpoints
test_items = {
  "item_1" : {
    "id" : "24CC73BD-3A88-4AD7-B9B4-5C01AEC2456E",
    "group" : "group 1",
    "fields" : {
      "title" : "term frequency inverse document frequency",
      "description" : "In information retrieval, tf–idf, TF*IDF, or TFIDF, short for term frequency–inverse document frequency, is a numerical statistic that is intended to reflect how important a word is to a document in a collection or corpus.[1] It is often used as a weighting factor in searches of information retrieval, text mining, and user modeling. The tf–idf value increases proportionally to the number of times a word appears in the document and is offset by the number of documents in the corpus that contain the word, which helps to adjust for the fact that some words appear more frequently in general. tf–idf is one of the most popular term-weighting schemes today. A survey conducted in 2015 showed that 83% of text-based recommender systems in digital libraries use tf–idf. Variations of the tf–idf weighting scheme are often used by search engines as a central tool in scoring and ranking a document's relevance given a user query. tf–idf can be successfully used for stop-words filtering in various subject fields, including text summarization and classification. One of the simplest ranking functions is computed by summing the tf–idf for each query term; many more sophisticated ranking functions are variants of this simple model",
    }
  },
  "item_2" : {
    "id" : "37BBB678-4E40-43AC-998D-454E667AEDBF",
    "group" : "group 1",
    "fields" : {
      "title" : "Information retrieval",
      "description" : "Information retrieval (IR) is the process of obtaining information system resources that are relevant to an information need from a collection of those resources. Searches can be based on full-text or other content-based indexing. Information retrieval is the science of searching for information in a document, searching for documents themselves, and also searching for the metadata that describes data, and for databases of texts, images or sounds. Automated information retrieval systems are used to reduce what has been called information overload. An IR system is a software system that provides access to books, journals and other documents; stores and manages those documents. Web search engines are the most visible IR applications.",
    }
  },
  "item_3" : {
    "id" : "F2FC84A3-9A0A-48A9-87EF-07C752C8E5B4",
    "group" : "group 1",
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
    "group" : "group 1",
    "fields" : {
      "title" : "Information overload",
      "description" : "Information overload (also known as infobesity,[1][2] infoxication,[3] information anxiety,[4] and information explosion[5]) is the difficulty in understanding an issue and effectively making decisions when one has too much information (TMI) about that issue,[6] and is generally associated with the excessive quantity of daily information. The term \"Information overload\" was first used in Bertram Gross' 1964 book, The Managing of Organizations,[7] and was further popularized by Alvin Toffler in his bestselling 1970 book Future Shock.[8] Speier et al. (1999) said that if input exceeds the processing capacity, information overload occurs, which is likely to reduce the quality of the decisions.[9] In a newer definition, Roetzel (2019) focuses on time and resources aspects. He states that when a decision-maker is given many sets of information, such as complexity, amount, and contradiction, the quality of its decision is decreased because of the individual’s limitation of scarce resources to process all the information and optimally make the best decision.[10] The advent of modern information technology has been a primary driver of information overload on multiple fronts: in quantity produced, ease of dissemination, and breadth of the audience reached. Longstanding technological factors have been further intensified by the rise of social media and the attention economy, which facilitates attention theft.[11][12] In the age of connective digital technologies, informatics, the Internet culture (or the digital culture), information overload is associated with over-exposure, excessive viewing of information, and input abundance of information and data.",
    }    
  }
}

test_status_requested = datetime.datetime(2021, 9, 10, 8, 0, 36, 424175).isoformat()
test_status_started = datetime.datetime(2021, 9, 10, 10, 1, 27, 593804).isoformat()
test_status_ended = datetime.datetime(2021, 9, 10, 13, 26, 17, 91609).isoformat()

test_status = {
  'not_run_yet' : {
    "id" :  "4D983232-8F13-4AD0-9933-51348379497D",
    "requested" : None,
    "started" : None,
    "ended" : None,
    "progressPercent" : 0,
    "progressDescription" : "",
    "inProgress" : False
  },
  'requested' : {
    "id" :  "C4B583B7-85C8-4C1E-83C3-1B23DBC3353C",
    "requested" : test_status_requested,
    "started" : None,
    "ended" : None,
    "progressPercent" : 0,
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
    "progressPercent" : 1,
    "progressDescription" : "Fake weight computation",
    "inProgress" : False
  }
}