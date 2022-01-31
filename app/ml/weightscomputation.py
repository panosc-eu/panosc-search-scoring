from app.models.compute import ComputeStatusModel
from typing import Union
from time import sleep
#import pandas as pd
import numpy as np
import json
from pymongo import InsertOne, UpdateOne, DeleteOne
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from uuid import uuid4

from app.models.weights import WeightModel
import app.ml.preprocessItemsText as pit
import app.ml.tf_iduf as tf_iduf
from ..common.utils import getCurrentTimestamp,debug
from ..common.database import COLLECTION_STATUS, COLLECTION_TF, COLLECTION_IDF, COLLECTION_ITEMS


_get_uuid = lambda: str(uuid4())

class WC():

  # database objects
  _config = None
  _db = None
  _items_coll = None
  _status_coll = None
  _tf_coll = None
  _idf_coll = None

  # group we need to compute the weights for
  _group = None

  # list of items or items_ids
  _items_to_be_updated = None
  _new_items = None
  _update_items = None
  _delete_items = None
  _terms_list = None
  _TF = None
  _IDF = None
  _rows = None
  _cols = None
  _items_id_remove_tf = []
  _terms_update = []

  _timestamp = None


  # logs of actions
  _logs = []

  
  # ---------------------
  def __init__(
      self,
      config, 
      database, 
      items_collection = COLLECTION_ITEMS, 
      status_collection = COLLECTION_STATUS,
      tf_collection = COLLECTION_TF,
      idf_collection = COLLECTION_IDF
  ):
    self._config = config
    self._db = database
    self._items_coll = self._db[items_collection] \
      if isinstance(items_collection,str) \
      else items_collection
    self._status_coll = self._db[status_collection] \
      if isinstance(status_collection,str) \
      else status_collection
    self._tf_coll = self._db[tf_collection] \
      if isinstance(tf_collection,str) \
      else tf_collection
    self._idf_coll = self._db[idf_collection] \
      if isinstance(idf_collection,str) \
      else idf_collection

    self._items = []


  # --------------------
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
      "inProgress" : inProgress,
      "incrementalWeightsComputation" : self._config.incrementalWeightsComputation
    }
    # add additional fields
    if started is not None:
      status['started'] = started
    if ended is not None:
      status['ended'] = ended
    # check that typing is correct
    ComputeStatusModel(**status)
    # update status in database
    res = await self._status_coll.update_many( 
      {}, 
      { 
        "$set" : status
      },
      upsert = True
    )
    print(res)


  # -------------------
  # 
  async def groups_list(self):
    """
    returns the list of unique group present in the items collections
    """
    await self._updateStatus(0.05,"Loading groups")
    # create aggregation pipeline
    pipeline = []
    # check if we have 
    if self._items and len(self._items):
      # user specified the list of items that we need to update the weights for
      groups = list(set(
        [item['group'] for item in self._items]
      ))

    else:
      # needs to extract groups from database
      # run aggregation
      res = await self._items_coll.aggregate(
        [
          {'$project' : {
            '_id' : 0,
            'group' : { "$ifNull": [ "$group", "default"] }
          }},
          {'$group' : {
            '_id' : None,
            'groups' : { "$addToSet" : "$group" }
          }}  
        ] 
      ) \
        .to_list(length=None)
      groups = res[0]['groups']

    # updates status
    await self._updateStatus(0.06,"Found {} groups".format(len(groups)))
    return groups


  # --------------------
  #
  async def select_group(self,group=None):
    """
    Set the group we want to compute the weights from
    """
    self._group = group
    await self._updateStatus(0.10,"Group set to {}".format(group))
    

  # --------------------
  #
  async def load_items(self):
    """
    Load items from database if needed
    """
    await self._updateStatus(0.15,"Loading items for group {}".format(self._group))

    # load all the items to be scored from the database
    # and save them in standard python list.
    # each item has the following fields
    # - _id
    # - group
    # - fields
    # - terms
    pipeline = []
    if self._group == 'default':
      pipeline.append({
        '$match' : {
          '$or' : [
            { "group" : { '$exists' : False } },
            { "group" : "default" }
          ]
        }
      })
    elif self._group:
      pipeline.append({
        '$match' : {
          "group" : self._group
        }
      })

    temp = {
      '$project' : {
        '_id' : 0,
        'item_id' : '$_id',
        'group' : { '$ifNull' : [ "$group", "default" ]},
        'terms' : 1
      }
    }
    pipeline.append(temp)

    list_cursor = await self._items_coll.aggregate(pipeline) \
      .to_list(length=None)

    # load all selected items
    self._items_to_be_updated = [item for item in list_cursor]

    # update status in database
    await self._updateStatus(0.16,"{} items loaded".format(len(self._items_to_be_updated)))



  # -------------------
  #
  async def compute_TF(self):
    """
    compute weights TF for terms
    """
    # update status in database
    await self._updateStatus(0.20,"Computing weights TF")

    # computes weights for pair item,term
    (self._TF,self._weights_rows,self._weights_cols) = tf_iduf.TF(self._items)

    # updates the list of terms to update
    self._terms_update += self._weights_cols

    # update status in database
    await self._updateStatus(0.21,"Weights TF computed")


  # -------------------
  #
  async def save_TF(self):
    """
    save weights TF in database
    """
    # update status in database
    await self._updateStatus(0.25,"Preparing weights TF for database update")

    self._timestamp = getCurrentTimestamp()

    # extract data and position from sparse matrix
    data = self._TF.data
    (rows,cols) = self._TF.nonzero()
    # convert to a triplet item, term, value
    db_operations = [
      UpdateOne(
        {
          'term' : self._weights_cols[cols[i]],
          'itemId' : self._weights_rows[rows[i]][1],
          'group' : self._weights_rows[rows[i]][0]
        },
        {
          'timestamp' : self._timestamp,
          'TF' : data[i]
        },
        upsert=True
      )
      for i
      in range(rows.shape[0])
    ]

    await self._updateStatus(0.26,"Saving weights")
    res = await self._TF_coll.bulk_write(db_operations)

    # update status in database
    await self._updateStatus(0.27,"Weights updated")


  # -------------------
  #
  async def remove_old_TF(self):
    # remove older version of TF weights

    await self._updateStatus(0.30,"Deleting old TF weights")
    res = await self._TF_coll.delete_many(
      {
        'itemGroup' : self._group , 
        'timestamp' : { "$lt" : self._timestamp }
      }
    )
    await self._updateStatus(0.31,"Old TF weights deleted")



  # -------------------
  #
  async def set_items(self,new_items=[],update_items=[],delete_items=[]):
    """
    set the list of items that were inserted new, updated or deleted
    """
    # partial lists
    self._new_items = new_items
    self._update_items = update_items
    self._delete_items = delete_items

    # list of items that needs the weight recomputed
    self._items_to_be_updated = new_items + update_items

    # list the ids of the item that will change fields
    # and the ones that will be removed
    self._items_id_remove_tf = [
      item['itemId'] 
      for item 
      in  self._update_items
      if 'fields' in item.keys()
    ] + [
      item['itemId'] if isinstance(item,dict) else item
      for item 
      in self._delete_items
    ]

    self._terms_update = []

    await self._updateStatus(0.35,"Loaded {} items".format(len(self._items_list)))


  # -------------------
  # 
  async def load_terms_for_updated_items(self):
    # load all the terms that are currently in the items 
    # that are going to be updated or deleted

    await self._updateStatus(0.40,"Loading terms for {} items to be updated".format(len(self._items_id_remove_tf)))

    # build the pipeline
    pipeline = [
      {
        '$match' : {
          '$expr' : {
            '$in' : [ '$_id', self._items_id_remove_tf ]
          }
        }
      },
      {
        '$unwind' : '$terms'
      },
      {
        '$project' : {
          '_id' : 0,
          'group' : { '$ifNull' : [ "$group", "default" ]},
          'terms' : 1
        }
      },
      {
        '$group' : {
          '_id' : { 'group' : '$group', 'term' : '$terms' },
          'count' : { '$sum' : 1 }
        }
      },
      {
        '$project' : {
          '_id' : 0,
          'group' : '$_id.group',
          'term' : '$_id.term'
        }
      }
    ]

    list_cursor = await self._items_coll.aggregation(pipeline) \
      .to_list(length=None)

    # load all selected items
    self._terms_update = list(set(
      self._terms_update + [term for term in list_cursor]
    )) 

    # update status in database
    await self._updateStatus(0.41,"Loaded {} terms".format(len(self._terms_update)))



  # -------------------
  # 
  async def delete_TF_for_updated_terms(self):
    # remove TF weights that related to updated or deleted items

    # update status in database
    await self._updateStatus(0.45,"Deleting obsolete TF weights")

    await self._tf_coll.delete({'_id' : { '$in' : self._items_to_be_updated}})    

    await self._updateStatus(0.46,"Obsolete TF weights deleted")


  # -------------------
  #
  async def delete_all_IDF(self):
    # delete all teh IDF weights
    # update status in database
    await self._updateStatus(0.50,"Deleting all IDF weights")

    await self._idf_coll.delete({})    

    await self._updateStatus(0.51,"Deleted all IDF weights")



  # -------------------
  # 
  async def delete_IDF_for_updated_terms(self):
    # remove TF weights that related to updated or deleted items

    # update status in database
    await self._updateStatus(0.55,"Deleting obsolete IDF weights for {} updated terms".format(len(self._terms_update)))

    db_operations = [
      DeleteOne(
        { '$and' : [
            { 'term' : t[1] },
            { 'group' : t[0] }
          ]}
      )
      for t
      in self._terms_update
    ]
    res = await self._idf_coll.bulk_write(db_operations)

    await self._updateStatus(0.56,"IDF weights for updated terms deleted")


  # -------------------
  # 
  async def compute_and_save_IDF(self):
    # compute and save IDF weights
    # list of terms per group has to be ready

    await self._updateStatus(0.60,"Updating IDF weights")

    # prepare expression for matching
    list_match_condition = [
      {
        '$and' : [
          { '$in' : [ '$term',  i[1] ] },
          { '$eq' : [ '$group', i[0] ] }
        ]
      }
      for i
      in self._terms_update
    ]
    match_condition = list_match_condition[0] \
      if len(list_match_condition) \
      else { '$or' : list_match_condition }
    # prepare the pipeline for the aggregation
    pipeline = [
      {
        '$match' : {
          '$expr' : list_match_condition
        }
      },
      {
        '$group' : {
          '_id' : { 'term' : '$term', 'group' : '$group' },
          'cdt' : { '$sum' : 1 }
        }
      },
      {
        '$lookup' : {
          'from' : COLLECTION_ITEMS,
          'let' : { 'group' : '$_id.group' },
          'pipeline' : [
            {
              '$match' : {
              '$expr' : {
                '$eq' : [ '$group' , '$$group' ]
                }
              }
            },
            {
              '$count' : 'count'
            }
          ],
          'as' : 'cd'
        }
      },    
      {
        '$project' : {
          '_id' : 0,
          'term' : '$_id.term',
          'group' : '$_id.group',
          'cd' : { '$first' : '$cd.count' },
          'cdt' : '$cdt',
        }   
      },
      {
        '$project' : {
          '_id' : 0,
          'term' : 1,
          'group' : 1,
          'timestamp' : self._timestamp,
          'IDF' : { '$log10' : { '$sum' : [ 1, { '$divide' : [ '$cd', '$cdt' ] } ] } }
        }   
      },
      {
        '$merge' : {
          'into' : 'IDF',
          'on' : [ 'group' , 'term' ],
          'whenMatched' : 'replace',
          'whenNotMatched' : 'insert'
        }
      }
    ]
    # run aggregation
    # res should be empty as we save the results directly with $merge
    res = self._tf_coll.aggregation(pipeline)

    await self._updateStatus(0.61,"IDF weights updated")



  # --------------------
  #
  @classmethod
  async def runOfflineWorkflow(
      cls, 
      config, 
      db
  ):
    """
    run the complete workflow to compute TF and IDF completely offline
    """
    # instantiate class for weight computation
    wc = cls(
      config, 
      db
    )
    # update status to started
    await wc._updateStatus(0,"Weights computation started",started=getCurrentTimestamp())
    
    # get list of groups/corpus
    groups = await wc.groups_list()
    # loop on all the groups and for each computes the weights
    for group in groups:
      await wc.select_group(group)
      await wc.load_items()
      await wc.compute_TF()
      await wc.save_TF()
      await wc.delete_all_IDF()
      await wc.compute_and_save_IDF()


    # update status to completed
    await wc._updateStatus(
      1.00,
      'All weights computed and updated',
      ended=getCurrentTimestamp(),
      inProgress=False)

    return wc


  @classmethod
  async def runIncrementalWorkflow(
      cls, 
      config, 
      db,
      new_items=[],
      update_items=[],
      delete_items=[]
  ):
    """
    run the incremental workflow on items just inserted, updated or deleted
    """
    # instantiate class for weight computation
    wc = cls(
      config, 
      db
    )

    # run computation for all items independently from the group they belong
    await wc.select_group(None)
    await wc.set_items(new_items=new_items,update_items=update_items,delete_items=delete_items)
    await wc.load_terms_for_updated_items()
    await wc.delete_TF_for_updated_terms()
    await wc.delete_IDF_for_updated_terms()
    await wc.compute_TF()
    await wc.save_TF()
    await wc.compute_and_save_IDF()

    return wc