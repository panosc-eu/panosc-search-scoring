#
# config class

import os
import json

from . import utils


class Config:

  tsStarted = utils.getCurrentTimestamp()
  tsCurrent = None
  uptime = None

  # information returned when root path is called
  rootInfo = {}

  # configuration
  config = {
    "database" : "pss",
    "mongodb_url" : "",
    "port" : 8000,
    "application" : "PSS",
    "description" : "PaNOSC search scoring",
    "version" : "v0-alpha",
    "waitToStartCompute" : 5,
    "debug" : False
  }

  # list of environmental variables
  env_variables = {
    "mongodb_url" : "str", 
    "port" : "int",
    "database" : "str", 
    "application" : "str", 
    "description" : "str", 
    "version" : "str",
    "waitToStartCompute" : "int",
    "debug" : "bool"
  }


  def __init__(self,config_file="./config/pss_config.json") -> None:
    # load configuration from file if exists 
    # or from environment variables 

    # file first
    if config_file and os.path.exists(config_file):
      with open(config_file,'r') as fh:
        config_from_file = json.load(fh)
        self.config = {
          **self.config,
          **config_from_file
        }

    # env variables next
    for var in self.env_variables.keys():
      env_var = "PSS_" + var.upper()
      env_value = os.getenv(env_var)
      if env_value is not None:
        if self.env_variables[var] == 'int':
          self.config[var] = int(env_value)
        elif self.env_variables[var] == 'bool':
          self.config[var] = bool(env_value)
        else:
          self.config[var] = env_value

    # set root information
    for info in ["application", "description", "version"]:
      self.rootInfo[info] = self.config[info]
    self.rootInfo["started-time"] = utils.getCurrentIsoTimestamp(self.tsStarted)
    

  def getCurrentRootInfo(self):
    self.tsCurrent = utils.getCurrentTimestamp()
    self.uptime = self.tsCurrent - self.tsStarted

    return { 
      **self.rootInfo,
      **{
        "current-time" : utils.getCurrentIsoTimestamp(self.tsCurrent),
        "uptime" : str(self.uptime)
      }
    }

  def __getattr__(self, attr):
    if attr in self.config.keys():
      return self.config[attr]
    raise(AttributeError("Config property not found"))
