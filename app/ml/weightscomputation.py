from time import sleep
import pandas as pd
import numpy as np
import json

import preprocessItemsText as pit
import tf_iduf


class WC():

  # database objects
  _config : None
  _db: None
  _items_coll: None
  _status_coll: None

  # dataframe with items to compute weights on
  _items: None
  _weights: None

  
  #
  def __init__(self,config, database, items_collection, status_collection):
    self._config = config
    self._db = database
    self._items_coll = self._db[items_collection] if isinstance(items_collection,str) else items_collection
    self._status_coll = self._db[status_collection] if isinstance(status_collection,str) else status_collection


  #
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


  # --------------------
  #
  def load(self):
    """
    Load items from database
    """
    self._updateStatus(0.10,"Loading items")

    # load all the items to be scored from the database
    list_cursor = self._coll.find({})

    # save them in a dataframe
    self._items = pd.DataFrame(list(list_cursor))

    # update status in database
    self._updateStatus(0.20,"{} items loaded".format(len(self._items)))


  #
  def extract(self):
    """
    Extract terms from items
    """
    # update status in database
    self._updateStatus(0.30,"Extracting terms")

    # combine meaningful fields for each item and extract terms
    self._items['terms'] = self._items.apply(pit.preprocessItemText,axis=1)

    # update status in database
    self._updateStatus(0.40,"Terms extracted")
    

  #
  def compute(self):
    """
    compute weights for terms
    """
    # update status in database
    self._updateStatus(0.50,"Computing weights")

    # computes weights for pair item,term
    self._weights = tf_iduf.TF_IDuF(self._items)

    # update status in database
    self._updateStatus(0.60,"Weights computed")


  #
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

