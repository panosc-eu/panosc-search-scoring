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


  def _extract_query_terms(self):
    # extract search terms from query
    self._query_terms = pit.preprocessItemText(self._request['query'])

  
  async def _load_weights(self):
    # load weights that refer to the query terms and the items passed
    # if not item ids have been passed, we use all items
    # same with the group
    self._db_query = [{
      'term' : {
        '$in' : self._query_terms
      }
    }]

    # check if we have the list of items id
    if self._request['itemIds']:
      self._db_query.append({
        'itemId' : { '$id' : self._request['itemIds'] }
      })

    if self._request['group']:
      self._db_query.append({
        'itemGroup' : self._request['group']
      })

    # query ready
    list_cursor = await self._weights_coll.find(
      self._db_query,
      { 
        '_id' : 0, 
        'timestamp': 0,
        'itemGroup' : 0
      }
    ).to_list(length=None)

    # save them in a dataframe
    self._df_weights = pd.DataFrame(list_cursor) \
      .set_index(['itemId','term']) \
      .unstack(level=-1)

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


  def _compute_scores(self):
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
    return self._df_scores.to_dict(orient='records')


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
      request.dict(),
      db,
      weights_coll
    )

    sc._ts_started = getCurrentTimestamp()
    # preprocess query: extrat terms
    sc._extract_query_terms()

    # load weights from database
    sc._load_weights()

    # compute scores
    sc._compute_scores()
    sc._ts_ended = getCurrentTimestamp()

    # return class
    return sc
