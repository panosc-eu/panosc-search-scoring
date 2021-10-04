from app.common.utils import getCurrentTimestamp
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


from ..models.score import ScoreRequestModel,ScoresResultsModel,ScoredItemModel
import app.ml.preprocessItemsText as pit


class SC:

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


  def __init__(self,request,db,weights_coll):
    self._request = request
    self._db = db
    self._weights_coll = weights_coll


  async def _extract_query_terms(self):
    # extract search terms from query
    self._query_terms = pit.preprocessItemText(self._request['query'])

  
  async def _load_weights(self):
    # load weights that refer to the query terms and the items passed
    # if not item ids have been passed, we use all items
    # same with the group
    self._db_query = {
      'term' : {
        '$in' : self._query_terms
      }
    }

    # check if we have the list of items id
    if self._request['itemIds']:
      self._db_query['itemId'] = { '$in' : self._request['itemIds'] }

    if self._request['group']:
      self._db_query['itemGroup'] = self._request['group']

    # query ready
    print(self._db_query)
    print(self._weights_coll.name)
    list_cursor = self._weights_coll.find(
      self._db_query,
      { 
        '_id' : 0, 
        'timestamp': 0,
        'itemGroup' : 0
      }
    )

    weights = [item for item in list_cursor]
    print(weights)

    # save them in a dataframe
    self._df_weights = pd.DataFrame(weights) \
      .set_index(['itemId','term']) \
      .unstack(level=-1) \
      .reset_index() 
    self._df_weights.columns = self._df_weights.columns.get_level_values(1)
    self._df_weights = self._df_weights \
      .rename(columns={'':'termId'}) \
      .set_index('termId') \
      .fillna(0)

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


  async def _compute_scores(self):
    # compute scores using cosine similarity

    # prepare data frame with query terms. All weights are set to 1
    self._df_query = pd.DataFrame(
      np.ones((1,len(self._query_terms))),
      columns=self._query_terms)
    # sort columns alphabetically
    self._df_query.sort_index(axis=1,inplace=True)

    # compute scores
    self._df_scores = pd.DataFrame(
      cosine_similarity(self._df_weights,self._df_query),
      index=self._df_weights.index,
      columns=["score"]
    ).sort_values(by="score",ascending=False)

    # checks if we need to trim the list
    if self._request['limit'] > 0:
      self._df_scores = self._df_scores.head(self._request['limit'])


  def getQueryTerms(self):
    return self._query_terms

  
  def getScores(self):
    return {
      k: v['score']
      for k, v
      in self._df_scores.to_dict(orient='index').items()
    }


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
      request: ScoreRequestModel,
      db,
      weights_coll
  ): 

    # initialize class
    sc = SC(
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
    await sc._compute_scores()
    sc._ts_ended = getCurrentTimestamp()

    # return class
    return sc
