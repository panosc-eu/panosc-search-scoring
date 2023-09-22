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
from collections import defaultdict

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
  _TF_rows = None
  _TF_cols = None
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
    #print(res)


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
        'id' : '$_id',
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

    if self._items_to_be_updated:
      # computes weights for pair item,term
      (self._TF,self._TF_rows,self._TF_cols) = tf_iduf.TF(self._items_to_be_updated)

      # updates the list of terms to update
      self._terms_update += self._TF_cols

      # update status in database
      await self._updateStatus(0.21,"Weights TF computed")

    else:
      self._TF = None
      # update status in database
      await self._updateStatus(0.22,"Weights TF computing not necessary")
      

  # -------------------
  #
  async def save_TF(self):
    """
    save weights TF in database
    """
    # update status in database
    await self._updateStatus(0.25,"Preparing weights TF for database update")

    if self._TF is not None:

      self._timestamp = getCurrentTimestamp()

      # extract data and position from sparse matrix
      #data = self._TF.data
      (rows,cols) = self._TF.nonzero()
      # convert to a triplet item, term, value
      db_operations = [
        UpdateOne(
          {
            'term' : self._TF_cols[cols[i]][1],
            'itemId' : self._TF_rows[rows[i]][1],
            'group' : self._TF_rows[rows[i]][0]
          },
          {
            '$set' : {
              'timestamp' : self._timestamp,
              'TF' : self._TF[rows[i],cols[i]]
            }
          },
          upsert=True
        )
        for i
        in range(rows.shape[0])
      ]

      await self._updateStatus(0.26,"Saving TF weights")
      res = await self._tf_coll.bulk_write(db_operations)

      # update status in database
      await self._updateStatus(0.27,"TF weights updated")

    else:
      # update status in database
      await self._updateStatus(0.28,"TF weights update no necessary")



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
  def _get_item_id(self,item):
    if isinstance(item,dict):
      if '_id' in item.keys():
        return(item['_id'])
      elif 'id' in item.keys():
        return(item['id'])
    return item

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
      self._get_item_id(item)
      for item 
      in  self._update_items
      if 'fields' in item.keys()
    ] + [
      self._get_item_id(item)
      for item 
      in self._delete_items
    ]

    self._terms_update = []

    await self._updateStatus(
      0.35,
      "Item set. New items {}, deleted items {}, updated items {}".format(
        len(self._new_items),
        len(self._delete_items),
        len(self._update_items)
      )
    )


  # -------------------
  # 
  async def load_terms_for_updated_items(self):
    # load all the terms that are currently in the items 
    # that are going to be updated or deleted

    await self._updateStatus(0.40,"Loading terms for {} items to be updated".format(len(self._items_id_remove_tf)))

    # build the pipeline
    pipeline = [
    #  {
    #    '$match' : {
    #      '$expr' : {
    #        '$in' : [ '$_id', self._items_id_remove_tf ]
    #      }
    #    }
    #  },
    #  {
    #    '$unwind' : '$terms'
    #  },
      {
        '$match' : {
          '$expr' : {
            '$in' : [ '$itemId', self._items_id_remove_tf ]
          }
        }
      },
      {
        '$project' : {
          '_id' : 0,
          'group' : { '$ifNull' : [ "$group", "default" ]},
          'term' : 1
        }
      },
      {
        '$group' : {
          '_id' : { 'group' : '$group', 'term' : '$term' },
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

    list_cursor = await self._tf_coll.aggregate(pipeline) \
      .to_list(length=None)

    # load all selected items
    self._terms_update = list(set(
      self._terms_update + [(i['group'],i['term']) for i in list_cursor]
    )) 

    # update status in database
    await self._updateStatus(0.41,"Loaded {} terms".format(len(self._terms_update)))



  # -------------------
  # 
  async def delete_TF_for_deleted_terms(self):
    # remove TF weights that related to deleted items

    # update status in database
    await self._updateStatus(0.45,"Deleting obsolete TF weights")

    res = await self._tf_coll.delete_many({'itemId' : { '$in' : self._items_id_remove_tf}})    

    await self._updateStatus(0.46,"Obsolete TF weights deleted")


  # -------------------
  #
  async def delete_all_IDF(self):
    # delete all teh IDF weights
    # update status in database
    await self._updateStatus(0.50,"Deleting all IDF weights")

    await self._idf_coll.delete_many({})    

    await self._updateStatus(0.51,"Deleted all IDF weights")



  # -------------------
  # 
  async def delete_IDF_for_updated_terms(self):
    # remove TF weights that related to updated or deleted items

    # update status in database
    await self._updateStatus(0.55,"Deleting obsolete IDF weights for {} updated terms".format(len(self._terms_update)))

    # check if we
    if len(self._terms_update)>0:
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

    else:

      await self._updateStatus(0.56,"no IDF weights to be deleted")



  # -------------------
  # 
  async def compute_and_save_IDF(self):
    # compute and save IDF weights
    # list of terms per group has to be ready

    await self._updateStatus(0.60,"Updating IDF weights")

    # prepare expression for matching
    reshape_cond = defaultdict(lambda: [])
    for i in self._terms_update:
        reshape_cond[i[0]].append(i[1])
    list_match_condition = [
      {
        '$and' : [
          { '$in' : [ '$term' , list(set(l)) ] },
          { '$eq' : [ '$group', g ] }
        ]
      }
      for g,l
      in reshape_cond.items()
    ]
    list_match_condition = list_match_condition[0] \
      if len(list_match_condition) == 1 \
      else { '$or' : list_match_condition }
    # prepare the pipeline for the aggregation
    # make sure that you have the correct index created on the weights_idf
    #db.weights_idf.createIndex( { 'group': 1, 'term': 1 }, { 'unique': true, "name" : "weights_idf" })
    #
    # [
    #  {'$match': {'$expr': {'$and': [{'$in': ['$term', ['advantag', 'address', 'mean', 'post', 'faster', 'use', 'fourteen', 'mention', 'cours', 'instruct', 'articl', 'two', 'new', 'take', 'forti', 'sixty', 'reed', 'machin', 'twelv', 'mode', 'rewritten', 'six', 'video', 'seven', '1993apr15', 'q800', 'slightli', 'write', 'adam', 'byte', 'especkma', 'recal', 'eighty', 'fill', 'command', 'c650', 'insid', 'rom', 'speckman', 'hundr', 'word', 'eight', 'fetch', 'sinc', 'centri', 'thousand', 'quadra', 'versu', 'text', 'erik', 'see', 'dale', 'quickdraw', 'acceler', 'edu', 'one', 'c610', 'macus', 'time']]}, {'$eq': ['$group', 'default']}]}}},
    #  {'$group': {'_id': {'term': '$term', 'group': '$group'}, 'cdt': {'$sum': 1}}},
    #  {'$project': { '_id': 0, 'term' : '$_id.term', 'group': '$_id.group', 'cdt': 1 }},
    #  {'$lookup': {'from': 'items', 'let': {'item_group': '$group'}, 'pipeline': [{'$match': {'$expr': {'$eq': ['$group', '$$item_group']}}}, {'$count': 'count'}], 'as': 'cd'}},
    #  {'$project': {'_id': 0, 'term': 1, 'group': 1, 'cd': {'$first': '$cd.count'}, 'cdt': '$cdt'}},
    #  {'$project': {'_id': 0, 'term': 1, 'group': 1, 'IDF': {'$log10': {'$sum': [1, {'$divide': ['$cd', '$cdt']} ]}}}},
    #  {'$merge': {'into': 'weights_idf', 'on': ['group', 'term'], 'whenMatched': 'replace', 'whenNotMatched': 'insert'}}
    # ]
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
        '$project': {
          '_id': 0,
          'term' : '$_id.term',
          'group': '$_id.group',
          'cdt': 1
        }
      },
      {
        '$lookup' : {
          'from' : COLLECTION_ITEMS,
          'let' : { 'item_group' : '$group' },
          'pipeline' : [
            {
              '$match' : {
              '$expr' : {
                '$eq' : [ '$group' , '$$item_group' ]
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
          'term' : 1,
          'group' : 1,
          'cd' : { '$first' : '$cd.count' },
          'cdt' : '$cdt',
        }   
      },
      {
        '$project' : {
          '_id' : 0,
          'term' : 1,
          'group' : 1,
          'timestamp' : self._timestamp.isoformat(),
          'IDF' : { '$log10' : { '$sum' : [ 1, { '$divide' : [ '$cd', '$cdt' ] } ] } }
        }   
      },
      {
        '$merge' : {
          'into' : COLLECTION_IDF,
          'on' : [ 'group' , 'term' ],
          'whenMatched' : 'replace',
          'whenNotMatched' : 'insert'
        }
      }
    ]
    # run aggregation
    # res should be empty as we save the results directly with $merge
    debug(self._config,pipeline)
    res = await self._tf_coll.aggregate(pipeline).to_list(None)

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
    '''
    run the incremental workflow on items just inserted, updated or deleted

    :param config: configuration structure
    :param db: database connection
    :param new_items: list of the new items just inserted in the database
    :param update_items: list of the items that have been updated
    :param delete_items: list of the ids of items that have been deleted
    :return:
    '''


    # instantiate class for weight computation
    wc = cls(
      config, 
      db
    )

    debug(config,"Starting weight computation");

    # run computation for all items independently from the group they belong
    await wc.select_group(None)
    await wc.set_items(new_items=new_items,update_items=update_items,delete_items=delete_items)
    await wc.load_terms_for_updated_items()
    await wc.delete_TF_for_deleted_terms()
    await wc.delete_IDF_for_updated_terms()
    await wc.compute_TF()
    await wc.save_TF()
    await wc.compute_and_save_IDF()
    debug(config,"Done weight computation");

    # update status to completed
    await wc._updateStatus(
      1.00,
      'All weights computed and updated',
      ended=getCurrentTimestamp(),
      inProgress=False)
    
    return wc
