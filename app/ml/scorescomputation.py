from operator import itemgetter
from pydantic import utils
from app.common.utils import getCurrentTimestamp
#import pandas as pd
from scipy.sparse import coo_matrix
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


from ..models.score import ScoreRequestModel,ScoresResultsModel,ScoredItemModel
import app.ml.preprocessItemsText as pit
from ..common.utils import debug

QUERY_SINGLE_TERM_MAX_SCORE = 0.9

class SC:

  _config = None
  _request = None
  _db = None
  _weights_coll = None

  _db_query = None
  _query_terms = None

  _requested_items = []

  _v_scores = None
  _v_query = None
  _m_weights = None
  _b_non_zero_weights = False

  _ts_started = None
  _ts_ended = None


  def __init__(self,config,request,db,weights_coll):
    self._config = config
    self._request = request
    self._db = db
    self._weights_coll = weights_coll


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
    # if not item ids have been passed, we use all items
    # same with the group
    self._db_query = {
      'term' : {
        '$in' : self._query_terms
      }
    }

    # check if we have the list of items id
    if "itemIds" in self._request.keys() and self._request['itemIds']:
      self._db_query['itemId'] = { '$in' : self._request['itemIds'] }
      self._requested_items = self._request['itemIds']

    if "group" in self._request.keys() and self._request['group']:
      self._db_query['itemGroup'] = self._request['group']

    # query ready
    debug(self._config,'--- query')
    debug(self._config,self._db_query)
    debug(self._config,self._weights_coll.name)
    list_cursor = await self._weights_coll.find(
      self._db_query,
      { 
        '_id' : 0, 
        'timestamp': 0
      }
    ).to_list(None)
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
    self._row2item = sorted(list(
      set([item['itemId'] for item in weights] + self._requested_items)
    ))
    self._item2row = { i:r for r,i in enumerate(self._row2item) }

    # initialize the weight matrix to none
    self._m_weights = None
    self._b_non_zero_weights = False
    # if there are no items or all weights are zeros, 
    # we should not create the weight matrix
    if len(self._row2item) > 0 and len(weights) > 0:
      # we have some items and non zero weights
      debug(self._config,"Items found or passed in and non zero weights present")
      
      # save weights in sparse matrix.
      # columns = terms according to col2term
      # rows = items id according to row2item
      debug(self._config,'--- prep weights')
      matrixData = []
      matrixRow = []
      matrixCol = []
      for weight in weights:
        matrixData.append(weight['value'])
        matrixRow.append(self._item2row[weight['itemId']])
        matrixCol.append(self._term2col[weight['term']])

      self._m_weights = coo_matrix(
        (matrixData,(matrixRow,matrixCol)),
        shape=[len(self._row2item),len(self._col2term)]
      )
      self._b_non_zero_weights = True

      debug(self._config,self._m_weights.shape)

    else:
      debug(self._config,"Matrix is all zeros")
    

  async def _compute_scores(self):
    """
    compute scores using cosine similarity
    """
    debug(self._config,'score_computation._compute_scores')

    if self._b_non_zero_weights: 
      debug(self._config,"Items and non zero weights. Computing scores")
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

    else:
      debug(self._config,"No items or only zero weights. Nothing to compute")
      self._v_scores = []
      self._sorted_scores = []

    debug(self._config,self._v_scores)
    debug(self._config,self._sorted_scores)


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

    # initialize scores list
    scores = []
    if self._b_non_zero_weights:
      # we have items and non zero weights
    
      # extract data and position from sparse matrix
      data = self._v_scores.data
      (rows,cols) = self._v_scores.nonzero()

      # check if we have a limit
      limit = len(self._sorted_scores)
      if 'limit' in self._request.keys() and self._request['limit'] > 0:
        limit = min(limit,self._request['limit'])

      scores = [
        {
          'itemId': self._row2item[rows[i]],
          'score' : data[i]
        }
        for i
        in self._sorted_scores[0:limit]
      ]

    elif len(self._row2item) > 0:
      # we have items but all zero weights
      # all the scores are zero
      scores = [
        {
          'itemId' : itemId,
          'score' : 0.0
        }
        for itemId
        in self._row2item
      ]

    if not self._config.return_zero_scores:
      # remove zero score items
      scores = [
        item
        for item 
        in scores
        if item['score'] > 0
      ]

    return scores

  def getScoresLength(self):
    return len(self._sorted_scores)

  
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
      db,
      weights_coll
  ): 
    debug(config,'score_computation.runWorkflow')
    # initialize class
    sc = SC(
      config,
      request,
      db,
      weights_coll
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
