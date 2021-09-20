from ..models.score import ScoreRequestModel,ScoresResultsModel,ScoredItemModel


class SC:

  _request: None
  _db: None
  _coll: None

  _queryTerms: None

  _scores: None


  def __init__(self,request,db,coll):
    self._request = request
    self._db = db
    self._coll = coll


  def getQueryTerms(self):
    return self._queryTerms

  
  def getScores(self):
    return self._scores


  @staticmethod
  async def runWorkflow(
      request: ScoreRequestModel,
      db,
      coll
  ): 

    # initialize class
    sc = SC()

    # preprocess query: extrat terms

    # load weights from database

    # compute scores

    # return class
    return sc
