#
# library that implements the computation TF_ID(u)F 
# it is based on pandas dataframe
#

import math
import pandas as pd

#
def TF(row,terms_column='terms'):
  """
  Computes the term frequency given a dataframe row 
  where the column specifid in terms_column contains the terms extracted
  from the item's text

  Ouput:
  - a dictionary of the terms extracted with the related term frequency 
  """

  # number of word in the title of this dataset (aka row)
  nwords = float(len(row[terms_column]))
  # build output and return
  return {
    **{
      'itemId': row['itemId'],
      'length': nwords
    },
    **{
      word: row[terms_column].count(word)/nwords
      for word
      in set(row[terms_column])
    }
  }


#
def IDF(df):
  """
  Computes the inverse document frequency for each row of the pandas data frame
  provided in input

  Output:
  - return a dictionary with the IDF for each term extracted
  """
  # first compute length of the dataframe aka number of datasets provided by this provider
  nDocs = len(df)
  # prepare idf and return structure
  return {
      column: math.log10(1+nDocs/len(df[df[column]!=0]))
      for column 
      in df.drop(columns=['length','itemId']).columns.to_list()
  }


#
def TF_IDuF(dfItems,terms_column='terms'):
  """
  """
  
  # compute TF for this dataset
  dfTF = pd.DataFrame(
    dfItems.apply(
      TF,
      axis=1,
      terms_column=terms_column
    ) \
    .to_list()
  ) \
  .fillna(0)
  
  # compute IDF for this dataset
  dfIDF = pd.DataFrame(
    IDF(dfTF),
    index=[0]
  )
  
  # multiply each row of dfTF by the matching word IDF
  dfOutput = dfTF.mul(
    dfIDF.loc[
      dfIDF.index.repeat(len(dfTF))
    ] \
    .set_index(dfTF.index)
  )
  dfOutput = dfOutput.drop(columns=['length','itemId'])
  
  # add provider column and reset index
  dfOutput = pd.merge(
    dfOutput,
    dfTF[['itemId']],
    left_index=True,
    right_index=True
  )
  
  # set id as row index
  dfOutput.set_index('itemId',inplace=True)
  
  return dfOutput


