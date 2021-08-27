#
# all the functions that do not fit anywhere else but they are useful
#

from datetime import datetime

def getCurrentTimestamp():
  return datetime.now()

def getCurrentIsoTimestamp(ts = None):
  ts = getCurrentTimestamp() if ts is None else ts
  return ts.isoformat(timespec='microseconds')

