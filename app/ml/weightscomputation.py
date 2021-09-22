from time import sleep
import pandas as pd
import numpy as np
import json
from pymongo import UpdateOne

from app.models.weights import WeightModel
import app.ml.preprocessItemsText as pit
import app.ml.tf_iduf as tf_iduf
from ..common.utils import getCurrentTimestamp


class WC():

  # database objects
  _config : None
  _db: None
  _items_coll: None
  _status_coll: None
  _weights_coll: None

  # group we need to compute the weights for
  _group: None

  # dataframe with items to compute weights on
  _items: None
  _weights: None

  # logs of actions
  _logs = []

  
  #
  def __init__(
      self,
      config, 
      database, 
      items_collection, 
      status_collection,
      weights_collection
  ):
    self._config = config
    self._db = database
    self._items_coll = self._db[items_collection] if isinstance(items_collection,str) else items_collection
    self._status_coll = self._db[status_collection] if isinstance(status_collection,str) else status_collection
    self._weights_coll = self._db[weights_collection] if isinstance(weights_collection,str) else weights_collection


  #
  def _updateStatus(self, progress, message):
    # insert in logs
    self._logs.append("{}: {}".format(progress, message))
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


  # -------------------
  # 
  def groups_list(self):
    """
    returns the list of unique group present in the items collections
    """
    self._updateStatus(0.01,"Loading groups")
    groups =  list(self._items_coll.distinct("group"))
    self._updateStatus(0.02,"Found {} groups".format(len(groups)))
    return groups


  #
  def select_group(self,group):
    """
    Set the group we want to compute the weights from
    """
    self._group = group
    self._updateStatus(0.03,"Group set to {}".format(group))
    

  # --------------------
  #
  def load(self):
    """
    Load items from database
    """
    self._updateStatus(0.10,"Loading items for group {}".format(self._group))

    # load all the items to be scored from the database
    list_cursor = self._coll.find({"group" : self._group})

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
    self._updateStatus(0.70,"Preparing weights for database update")

    timestamp = getCurrentTimestamp()

    # check columns
    # convert to a triplet item, term, value
    updates = [
      UpdateOne(
        {
          'term' : weight['term'],
          'itemId' : weight['itemId'],
          'itemGroup' : self._group
        },
        {
          '$set' : {
            'timestamp' : timestamp,
            'value' : weight['value']
          }
        },
        upsert=True
      )
      for weight
      in self._weights.stack().reset_index().to_dict(orient='record')
    ]
    self._updateStatus(0.75,"Saving weights")
    res = self._weights_coll.bulk_write(updates)

    self._updateStatus(0.80,"Deleting old weights")
    res = self._weights_coll.delete_many(
      {
        'group' : self._group , 
        'timestamp' : { "$lt" : timestamp }
      }
    )

    # update status in database
    self._updateStatus(0.85,"Weights updated")


  @classmethod
  def runWorkflow(
      cls, 
      config, 
      db, 
      items_coll,
      status_coll,
      weights_coll
  ):
    """
    run the complete work flow
    """
    wc = cls(
      config, 
      db, 
      items_coll,
      status_coll,
      weights_coll
    )
    for group in wc.groups_lists():

      wc.select_group(group)
      wc.load()
      wc.extract()
      wc.compute()
      wc.save()

    wc._updateStatus(1.00,'All weights computed and updated')

    return wc

