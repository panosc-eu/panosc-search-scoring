from pydantic import utils
from app.common.utils import getCurrentTimestamp
#import pandas as pd
from scipy.sparse import coo_matrix
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


from ..models.score import ScoreRequestModel,ScoresResultsModel,ScoredItemModel
import app.ml.preprocessItemsText as pit
from ..common.utils import debug
from app.common.database import COLLECTION_TF, COLLECTION_IDF


QUERY_SINGLE_TERM_MAX_SCORE = 0.9

class SC:

  _config = None
  _request = None
  _db = None
  _tf_coll = None
  _idf_coll = None

  _db_query = None
  _query_terms = None

  _v_scores = None
  _v_query = None
  _m_weights = None

  _ts_started = None
  _ts_ended = None


  def __init__(
    self,
    config,
    request,
    database,
    tf_collection = COLLECTION_TF,
    idf_collection = COLLECTION_IDF
  ):
    self._config = config
    self._request = request
    self._db = database
    self._tf_coll = self._db[tf_collection] \
      if isinstance(tf_collection,str) \
      else tf_collection
    self._idf_coll = self._db[idf_collection] \
      if isinstance(idf_collection,str) \
      else idf_collection


  async def _extract_query_terms(self):
    """
    """
    debug(self._config,'score_computation._extract_query_terms')
    # extract search terms from query
    self._query_terms = pit.preprocessItemText(self._request['query'])
    debug(self._config,self._query_terms)

  
  async def _load_weights(self):
    """
    """
    debug(self._config,'score_computation._load_weights')
    
    # load weights that refer to the query terms and the items passed
    # if no item ids have been passed, we use all items
    # same with the group
    match_conditions = [
      { 'term' : 
        { '$in' : self._query_terms }
      }
    ]
    # check if we have the list of items id
    if "itemIds" in self._request.keys() and self._request['itemIds']:
      match_conditions.append(
        { 'itemId' : { '$in' : self._request['itemIds'] } }
      )

    if "group" in self._request.keys() and self._request['group']:
      match_conditions.append(
        { 'itemGroup' : self._request['group'] }
      )

    if len(match_conditions) > 1:
      match_conditions = {
        "$and" : match_conditions
      }

    # build pipeline to retrieve TF, IDF and the combined weight
    self._db_pipeline = [
      {
        "$match" : match_conditions
      },
      {
        "$lookup" :{
          'from' : COLLECTION_IDF,
          'let' : { 'term' : '$term', 'group' : '$group' },
          'pipeline' : [
            {
              '$match' : {
                '$expr' : {
                  '$and' : [
                    { '$eq' : [ '$term' , '$$term' ]},
                    { '$eq' : [ '$group' , '$$group' ] }
                  ]
                }
              }
            }
          ],
          'as' : 'idf'
        }
      },
      {
        "$project" : {
          "_id" : 0,
          "term" : 1,
          "itemId" : 1,
          "group" : 1,
          "TF" : "$TF",
          "IDF" : "$idf.IDF",
          "weight" : { "$multiply" : [ "$TF", "$idf.IDF" ]}
        }
      }
    ]


    # query ready
    debug(self._config,'--- pipeline')
    debug(self._config,self._db_pipeline)
    list_cursor = await self._tf_coll.aggregate(self._db_pipeline) \
      .to_list(length=None)

    # load all selected items
    self._terms_update = list(set(
      self._terms_update + [term for term in list_cursor]
    )) 

    debug(self._config,list_cursor)
    weights = [item for item in list_cursor]
    debug(self._config,weights)

    # prepare columns and rows vectors
    # they allow us to go from column index to term
    # and from row to index
    self._col2term = sorted(list(
      set([item['term'] for item in weights] + self._query_terms)
    ))
    self._term2col = { t:c for c,t in enumerate(self._col2term) }
    self._row2item = sorted(list(set([[item['group'], item['itemId']] for item in weights])))
    self._item2row = { i:r for r,i in enumerate(self._row2item) }

    # save weights in sparse matrix.
    # columns = terms according to col2term
    # rows = items id according to row2item
    debug(self._config,'--- prep weights')
    matrixData = []
    matrixRow = []
    matrixCol = []
    for weight in weights:
      matrixData.append(weight['weight'])
      matrixRow.append(self._item2row[weight['itemId']])
      matrixCol.append(self._term2col[weight['term']])

    self._m_weights = coo_matrix((matrixData,(matrixRow,matrixCol)))
    debug(self._config,self._m_weights.shape)
    

  async def _compute_scores(self):
    """
    compute scores using cosine similarity
    """
    debug(self._config,'score_computation._compute_scores')

    # check how many terms are present in the query
    if (len(self._query_terms) > 1):

      # prepare matrix with with query terms. All weights are set to 1
      matrixData = []
      matrixCol = []
      for term in self._query_terms:
        matrixData.append(1)
        matrixCol.append(self._term2col[term])
      matrixRow = [0] * len(matrixCol)
    

      self._v_query = coo_matrix((matrixData,(matrixRow,matrixCol)))
      debug(self._config,self._v_query)

      # compute scores
      self._v_scores = cosine_similarity(self._m_weights,self._v_query,dense_output=False)

    else:
      # when the query has only one term
      # we cannot use the cosine similarity
      # as score, we will pass back the weight of the term within the items
      self._v_scores = self._m_weights
      self._v_scores = QUERY_SINGLE_TERM_MAX_SCORE*self._v_scores/self._v_scores.max()

    # sort elements from the most relevant to the least one
    self._sort_results()

    print(self._v_scores)
    print(self._sorted_scores)

    debug(self._config,self._v_scores)


  def _sort_results(self):
    # internal function to order the scores from the most relevant to the least relevant
    (rows,cols) = self._v_scores.nonzero()
    self._sorted_scores = [
      e1[0]
      for e1 
      in sorted(
        zip(
          rows,
          self._v_scores.data
        ),
        key = lambda e2: e2[1],
        reverse=True
      )
    ]


  def getQueryTerms(self):
    return self._query_terms

  
  def getScores(self):
    # extract data and position from sparse matrix
    data = self._v_scores.data
    (rows,cols) = self._v_scores.nonzero()

    # check if we have a limit
    limit = len(self._sorted_scores)
    if 'limit' in self._request.keys() and self._request['limit'] > 0:
      limit = min(limit,self._request['limit'])

    return [
      {
        'itemId': self._row2item[rows[i]],
        'score' : data[i]
      }
      for i
      in self._sorted_scores[0:limit]
    ]


  def getScoresLength(self):
    return self._v_scores.shape[0]

  
  @property
  def started(self):
    return self._ts_started

  
  @property
  def ended(self):
    return self._ts_ended


  @staticmethod
  async def runWorkflow(
      config,
      request: ScoreRequestModel,
      database,
      tf_collection = COLLECTION_TF,
      idf_collection = COLLECTION_IDF
  ): 
    debug(config,'score_computation.runWorkflow')
    # initialize class
    sc = SC(
      config,
      request,
      database,
      tf_collection,
      idf_collection
    )

    sc._ts_started = getCurrentTimestamp()
    # preprocess query: extrat terms
    await sc._extract_query_terms()

    # load weights from database
    await sc._load_weights()

    # compute scores
    #sc._df_scores = pd.DataFrame()
    await sc._compute_scores()
    sc._ts_ended = getCurrentTimestamp()

    # return class
    return sc
