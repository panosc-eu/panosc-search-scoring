#
# this is the library containing all the accessory NLP functions
# needed to extract terms from the items to be scored in the 
# PaNOSC federated search
#
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
import num2words
from nltk.stem import PorterStemmer
import datetime
import re
import json


# Load the english stop words from nltk
stop_words_t1 = stopwords.words('english')
#stop_words_t1.append('id')
stop_words = set(stop_words_t1)
del stop_words_t1

# punctuation symbols that we want to remove from the text
punctuation_symbols = "!\"#$%&()*+-,./:;<=>;?@[\]^_`{|}~\n–"

# instantiate a stemmer from nltk package
stemmer = PorterStemmer()


# remove punctuation symbols
def removePunctuation(instring,symbols):
  outstring = instring
  for symbol in symbols:
    outstring = outstring.replace(symbol, ' ')
  return outstring


# remove unicode characters that cannot be interpreted
def removeUnicode(instring):
  return re.sub('\\\\u\d\d\d\d', ' ', instring)


# remove stop words
def removeStopWords(instring):
  return ' '.join([item for item in instring.split(' ') if item not in stop_words])


# remove single quotes/apostrophy
def removeApostrophy(instring):
  return instring.replace("'", "")


# remove multiple consecutive spaces
def removeUnneededSpaces(instring):
  # remove consecutive spaces
  outstring = re.sub('  *',' ',instring)
  # remove preceding spaces
  outstring = re.sub('^ +','',outstring)
  # remove trailing spaces
  outstring = re.sub(' +$','',outstring)
  return outstring


# converts all the numbers to words
def convertWord2Number(inword):
  try:
      # tries to convert integers
      outword = num2words.num2words(int(inword))
  except:
      try:
          # tries to convert floats
          outword = num2words.num2words(float(inword))
      except:
          # input word is not a number, or at least we assume so
          outword = inword
      #end try/except
  #end try/except
  return outword


#
def convertSentence2Numbers(instring):    
  return ' '.join(convertWord2Number(word) for word in instring.split(' '))


# now we lemmatize each word of each entry
def stemmatize(instring,stemmer):
  return ' '.join([stemmer.stem(word) for word in instring.split(' ')])


def removeShortWords(instring):
  return ' '.join(
      [
          word
          for word
          in instring.split(' ')
          if len(word) > 1
      ]
  )


# preprocess each single entry
def preprocessItemText(item):
  """
  extract the meaningful fields from the item (which is passed in as a pandas dataframe row)
  Convert them in a string, using json.dumps
  and run all the preprocess steps as highlighted in the PaNOSC search scoring report
  """

  # check if input item is a string
  # if it is not, we assume that it is a panda dataframe row
  outstring = item if isinstance(item,str) else json.dumps(item['fields'])

  outstring = outstring.lower()
  outstring = removeUnicode(outstring)
  outstring = removePunctuation(outstring,punctuation_symbols)
  outstring = removeStopWords(outstring)
  outstring = removeApostrophy(outstring)
  outstring = removeUnneededSpaces(outstring)
  outstring = convertSentence2Numbers(outstring)
  outstring = removeStopWords(outstring)
  outstring = stemmatize(outstring,stemmer)
  outstring = removePunctuation(outstring,punctuation_symbols)
  outstring = removeUnneededSpaces(outstring)
  outstring = removeShortWords(outstring)
  
  return outstring.split(' ')



  