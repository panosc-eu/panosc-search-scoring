#
# library that implements the computation TF_ID(u)F 
# it is based on pandas dataframe
#

import math
#import pandas as pd
from collections import Counter
from itertools import chain
from typing import no_type_check
from scipy.sparse import coo_matrix
import numpy as np

#
def itemTF(item,terms_key='terms'):
  """
  Computes the term frequency given an item dictionary 
  where the value under the terms_key contains the terms extracted
  from the item's text

  Output:
  - a dictionary of the terms extracted with the related term frequency 
  """

  # instantiate a counter object
  c = Counter(item[terms_key])
  # number of unique terms found
  nut = len(c)
  # build output and return
  return {
    t: o/nut
    for t,o
    in c.items()
  }


# ---------------------------
#
def termIDF(numberOfItems,numberOfItemsForTerm):
  """
  Computes the inverse document frequency for the specific term

  Output:
  - return the IDF in floating point
  """
  return math.log10(1+numberOfItems/numberOfItemsForTerm)


# ---------------------------
#
def TF(items,terms_key='terms'):
  """
  Computes the TF value for all the terms extracted from each item

  Outputs:
  - TF     : scipy sparse matrix with the TF weights
  - rows   : python list with the items id present in TF_IDF rows
  - cols   : python list with the terms present in TF_IDF columns
  """
  
  # additional variables needed in the process
  termsSet = set()
  col2term = []
  term2col = {}
  row2item = []
  matrixData = []
  matrixRow = []
  matrixCol = []

  # loops on all the items of the dataset
  for item in items:

    # compute TF for all the terms found in the item
    tfCoefficients = itemTF(item,terms_key)

    # extract new terms from item terms list
    newTerms = list(
      set(
        [
          (item['group'],term)
          for term
          in tfCoefficients.keys()
        ]
      ) - termsSet)

    # add new terms to columns mapping
    col2term += newTerms

    # update terms to col convertion
    for term in newTerms:
      term2col[term] = col2term.index(term)

    # update terms set
    termsSet.update(newTerms)

    # add current item to row mapping
    row2item.append([item['group'], item['_id']])

    # prepares the variables to define the sparse matrix
    # we need to provide 3 different lists: data, the row and the col
    for term,tf in tfCoefficients.items():
      matrixData.append(tf)
      matrixRow.append(len(row2item)-1)
      matrixCol.append(term2col[(item['group'],term)])

  # create the sparse matrix for TF in column format which is best for multiplication
  matrixTF = coo_matrix((matrixData,(matrixRow,matrixCol))).tocsc()

  return (matrixTF, row2item, col2term)


#------------------
#
def TF_IDF(items,terms_key='terms'):
  """
  Computes the TF_IDF weights for all the terms extracted from each item

  Outputs:
  - TF_IDF : scipy sparse matrix with the TF_IDF weights
  - rows   : python list with the items id present in TF_IDF rows
  - cols   : python list with the terms present in TF_IDF columns
  """
  
  # compute the TF matrix
  (matrixTF, row2item, col2term) = TF(items,terms_key)

  # number of items
  numberOfItems = len(items)

  # create sparse vector for IDF
  vectorIDF = coo_matrix(
    np.array(
      [[
        termIDF(
          numberOfItems,
          (matrixTF.getcol(column)!=0).sum()
        )
        for column
        in range(len(col2term))
      ]]
    )
  ).tocsc()
  
  # create TF_IDF sparse matrix by multiply element by element 
  # the IDF vector to each row of the TF matrix
  # the resulting sparse matrix is converted to coo which is best 
  # fo retrieving the information to be saved in the database
  matrixTF_IDF = matrixTF.multiply(
    (
      coo_matrix(
        np.ones((numberOfItems,1))
      ) * vectorIDF
    ).tocsc()
  ).tocoo()
  
  return (matrixTF_IDF, row2item, col2term)


