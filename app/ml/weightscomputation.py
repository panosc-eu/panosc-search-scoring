from time import sleep

class WC():

  _config : None
  _db: None
  _coll: None

  def __init__(self,config, database, collection):
    self._config = config
    self._db = database
    self._coll = collection


  def _updateStatus(self, progress, message):
    # update status in database
    self._coll.update_many( 
      {}, 
      { 
        "$set" : { 
          "progressPercent" : progress,
          "progressDescription" : message
        }
      }
    )


  def load(self):
    """
    Load items from database
    """
    # update status in database
    self._updateStatus(0.20,"Loading items")


  def extract(self):
    """
    Extract terms from items
    """
    # update status in database
    self._updateStatus(0.40,"Extracting terms")

  def compute(self):
    """
    compute weights for terms
    """
    # update status in database
    self._updateStatus(0.60,"Computing weights")


  def save(self):
    """
    save weights in database
    """
    # update status in database
    self._updateStatus(0.80,"Saving weights")

    sleep(1)


  @classmethod
  def runWorkflow(cls, config, db, coll):
    """
    run the complete work flow
    """
    wc = cls(config, db, coll)
    wc.load()
    wc.extract()
    wc.compute()
    wc.save()

    return wc

