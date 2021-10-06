from pydantic import utils
from app.common.utils import getCurrentTimestamp
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


from ..models.score import ScoreRequestModel,ScoresResultsModel,ScoredItemModel
import app.ml.preprocessItemsText as pit
from ..common.utils import debug


class SC:

  _config = None
  _request = None
  _db = None
  _weights_coll = None

  _db_query = None
  _query_terms = None

  _df_scores = None
  _df_query = None
  _df_weights = None

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

    # save them in a dataframe.
    # it also pivot the dataframe so terms are in columns and rows are the items
    debug(self._config,'--- prep weights')
    self._df_weights = pd.DataFrame(weights) \
      .set_index(['itemGroup','itemId','term']) \
      .unstack(level=-1) \
      .reset_index()
    debug(self._config,self._df_weights)
    # adjust columns names
    columns = list(self._df_weights.columns.get_level_values(1))
    columns[0] = 'itemGroup'
    columns[1] = 'itemId'
    self._df_weights.columns = columns
    # re-set index and fill table with zeros
    self._df_weights = self._df_weights \
      .set_index(['itemGroup','itemId']) \
      .fillna(0)
    debug(self._config,self._df_weights)

    # add missing query terms
    self._df_weights[
      list(
        set.difference(
          set(self._query_terms),
          set(self._df_weights.columns)
        )
      )
    ] = 0

    # order columns in alphabetical order
    self._df_weights.sort_index(axis=1,inplace=True)
    debug(self._config,self._df_weights)


  async def _compute_scores(self):
    """
    compute scores using cosine similarity
    """
    debug(self._config,'score_computation._compute_scores')

    # prepare data frame with query terms. All weights are set to 1
    self._df_query = pd.DataFrame(
      np.ones((1,len(self._query_terms))),
      columns=self._query_terms)
    # sort columns alphabetically
    self._df_query.sort_index(axis=1,inplace=True)
    debug(self._config,self._df_query)

    # compute scores
    self._df_scores = pd.DataFrame(
      cosine_similarity(self._df_weights,self._df_query),
      index=self._df_weights.index,
      columns=["score"]
    ).sort_values(by="score",ascending=False)

    # checks if we need to trim the list
    if 'limit' in self._request.keys() and self._request['limit'] > 0:
      self._df_scores = self._df_scores.head(self._request['limit'])
    debug(self._config,self._df_scores)
    debug(self._config,self._df_scores.reset_index().head().to_dict(orient='records'))


  def getQueryTerms(self):
    return self._query_terms

  
  def getScores(self):
    return [
      {
        'group' : record['itemGroup'],
        'itemId': record['itemId'],
        'score' : record['score']
      }
      for record
      in self._df_scores.reset_index().to_dict(orient='records')
    ]


  def getScoresLength(self):
    return len(self._df_scores)

  
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
