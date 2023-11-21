from app.models.compute import ComputeStatusModel
from typing import Union
from time import sleep
#import pandas as pd
import numpy as np
import json
from pymongo import InsertOne
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from uuid import uuid4

from app.models.weights import WeightModel
import app.ml.preprocessItemsText as pit
import app.ml.tf_iduf as tf_iduf
from ..common.utils import getCurrentTimestamp,debug


_get_uuid = lambda: str(uuid4())

class WC():

  # database objects
  _config = None
  _db = None
  _items_coll = None
  _status_coll = None
  _weights_coll = None

  # group we need to compute the weights for
  _group = None

  # dataframe with items to compute weights on
  _items = None
  _weights = None
  _rows = None
  _cols = None

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
  async def _updateStatus(
      self, 
      progress: float, 
      message: str,
      started: Union[datetime, None] = None,
      ended: Union[datetime, None] = None,
      inProgress: bool = True
  ):
    # insert in logs
    self._logs.append("{}: {}".format(progress, message))
    # prepare status
    status = { 
      "progressPercent" : progress,
      "progressDescription" : message,
      "inProgress" : inProgress
    }
    # add additional fields
    if started is not None:
      status['started'] = started
    if ended is not None:
      status['ended'] = ended
    # check that typing is correct
    ComputeStatusModel(**status)
    # update status in database
    await self._status_coll.update_many( 
      {}, 
      { 
        "$set" : status
      }
    )


  # -------------------
  # 
  async def groups_list(self):
    """
    returns the list of unique group present in the items collections
    """
    await self._updateStatus(0.01,"Loading groups")
    res = await self._items_coll.aggregate(
      [
        {'$project' : {
          '_id' : 0,
          'group' : { "$ifNull": [ "$group", "default"] }
        }},
        {'$group' : {
          '_id' : 'groups_list',
          'groups' : { "$addToSet" : "$group" }
        }}
      ]
    ) \
      .to_list(length=None)
    groups = res[0]['groups']
    # groups =  list(await self._items_coll.distinct("group"))
    # self._updateStatus(0.02,"Checking for default group")
    # if 'default' not in groups
    #   default_items = list(self._items_coll.find({"group" : None}))
    #   if len(default_items) > 0:
    #     groups.append('default')
    await self._updateStatus(0.03,"Found {} groups".format(len(groups)))
    return groups


  #
  async def select_group(self,group):
    """
    Set the group we want to compute the weights from
    """
    self._group = group
    await self._updateStatus(0.05,"Group set to {}".format(group))
    

  # --------------------
  #
  async def load(self):
    """
    Load items from database
    """
    await self._updateStatus(0.10,"Loading items for group {}".format(self._group))

    # load all the items to be scored from the database
    # and save them in standard python list.
    # each item has the following fields
    # - _id
    # - group
    # - fields
    if self._group == 'default':
      list_cursor = await self._items_coll.find(
        { "$or" : [
          { "group" : { "$exists" : False } },
          { "group" : self._group }
        ]}
      ) \
        .to_list(length=None)
    else:
      list_cursor = await self._items_coll.find({"group" : self._group}).to_list(length=None)

    self._items = [item for item in list_cursor]

    # update status in database
    await self._updateStatus(0.20,"{} items loaded".format(len(self._items)))


  #
  async def extract(self):
    """
    Extract terms from items
    """
    debug(self._config,"weight_computation:extract")
    # update status in database
    await self._updateStatus(0.30,"Extracting terms")

    # combine meaningful fields for each item and extract terms
    # creates a new list of items with updated fields names
    # - itemId
    # - group
    # - terms
    self._items = [
      {
        'itemId' : item['_id'],
        'group'  : item['group'] if 'group' in item.keys() else 'default', 
        'terms'  : pit.preprocessItemText(item)
      }
      for item 
      in self._items
    ]
    debug(self._config,self._items)

    # update status in database
    await self._updateStatus(0.40,"Terms extracted")
    

  #
  async def compute(self):
    """
    compute weights for terms
    """
    # update status in database
    await self._updateStatus(0.50,"Computing weights")

    # computes weights for pair item,term
    (self._weights,self._weights_rows,self._weights_cols) = tf_iduf.TF_IDF(self._items)

    # update status in database
    await self._updateStatus(0.60,"Weights computed")


  #
  async def save(self):
    """
    save weights in database
    """
    # update status in database
    await self._updateStatus(0.70,"Preparing weights for database update")

    timestamp = getCurrentTimestamp()

    # extract data and position from sparse matrix
    data = self._weights.data
    (rows,cols) = self._weights.nonzero()
    # convert to a triplet item, term, value
    new_weights = [
      InsertOne(
        {
          '_id' : _get_uuid(),
          'term' : self._weights_cols[cols[i]],
          'itemId' : self._weights_rows[rows[i]],
          'itemGroup' : self._group,
          'timestamp' : timestamp,
          'value' : data[i]
        }
      )
      for i
      in range(rows.shape[0])
    ]

    await self._updateStatus(0.80,"Saving weights")
    res = await self._weights_coll.bulk_write(new_weights)

    await self._updateStatus(0.85,"Deleting old weights")
    res = await self._weights_coll.delete_many(
      {
        'itemGroup' : self._group , 
        'timestamp' : { "$lt" : timestamp }
      }
    )

    # update status in database
    await self._updateStatus(0.90,"Weights updated")


  @classmethod
  async def runWorkflow(
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
    # instantiate class for weight computation
    wc = cls(
      config, 
      db, 
      items_coll,
      status_coll,
      weights_coll
    )
    # update status to started
    await wc._updateStatus(0,"Weights computation started",started=getCurrentTimestamp())
    # get list of groups/corpus
    groups = await wc.groups_list()
    # loop on all the groups and for each computes the weights
    for group in groups:
      await wc.select_group(group)
      await wc.load()
      await wc.extract()
      await wc.compute()
      await wc.save()
    # update status to completed
    await wc._updateStatus(
      1.00,
      'All weights computed and updated',
      ended=getCurrentTimestamp(),
      inProgress=False)

    return wc

