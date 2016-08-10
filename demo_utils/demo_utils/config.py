'''
A module makes it easy to set up a configuration directory and read configurations files from that directory.

This module will look for a directory called `configuration` in the nearby directory structure. It will attempt to first read all files from this directory first, then it will look elsewhere.

See the python docs on ConfigParser for more information on the default config behavior.

This module also supports reading Ambari configurations in the same way that it writes configuration values

Currently it is not possible to write configurations (Python-style configs and Ambari XML).
'''
import os, ConfigParser, glob, sys
import xml.etree.ElementTree as ET


# readConfig
# Arguments : a relative path to the file
#
#  This function uses the working directory.
#  os.getcwd() is the working directory of the file/function
#  which called readConfig
#  The path to configFile is appended to the cwd
#
# All params are read as strings

def read_config(config_file):
  '''Read the configuration of a python style configuration file
  
  Args:
    config_file (str): The path to the configuration file. This can either be a fully qualified path or the path relative to your configuration directory
    
  Returns:
    dict: Configurations values stored under `[SECTION_KEY][PARAMETER_NAME]`
    '''
  
  path = get_path(config_file)
  
  config = ConfigParser.ConfigParser()
  config.read(path)
  params = {}
  
  for section in config.sections():
    params[section] = {}
    for key in config.options(section):
      params[section][key] = config.get(section, key)
  
  return params

def read_xml_config(config_file):
  '''Read an Ambari-style XML configuration file
  
    Args:
      config_file (str): The path to the configuration file. This can either be a fully qualified path or the path relative to your configuration directory.
    
    Returns:
      dict: A dictionary object where you can access the values via `[PARAM_KEY]`
    '''
  path = get_path(config_file)
  config_root = ET.parse(path).getroot()
  conf = {}
  # Get all property elements
  for prop in config_root.findall('property'):
    
    nm = prop.find('name')
    val = prop.find('value')
    if not (nm == None or val == None):
      conf[nm.text] = val.text
      
  return conf

# Raises an IOError if the file doesn't exist
# Returns the path to the file if it does
def get_path(config_file):
  '''Returns a fully qualified path for a configuration file. Will check inside configuration directory first.
  
  Args:
    config_file (str): The path to the configuration file. This can either be a fully qualified path or the path relative to your configuration directory.
    
  Returns:
    string: A string containing the full path to the configuration file. If the original
    
  Raises:
    IOError: Raised when the file can't be found in either the configuration directory or by the absolute path
  
  '''
  path = get_conf_dir() + config_file
  exists = False
  
  if os.path.isfile(path):
    exists = True
  elif os.path.isfile(config_file):
    path = config_file
    exists = True
    
  if not exists:
    raise IOError('Could not find file at ' + config_file + ' or ' + path)  
  
  return path
  
# returns a dict with dict['configurations'] containing
# another dict with a list of file names
# Under each filename is the parameters

def get_config():
  '''Mimicks the output of the Ambari resource_management library for extracting parameters form XML files.
  
  This function utilizes a configuration directory. After acquiring the path to the directory, the function will find all XML files (that should be formatted Ambari-style). It will then read all parameters and return a dict where every parameter can be accessed.
  
  Args:
    None
  
  Returns:
    dict: An object which houses the configuration params. Accessed by get_config()['configurations'][FILE_NAME][PARAM_NAME]
  '''
  conf = {}
  conf['configurations'] = {}
  
  conf_dir = get_conf_dir()
  dir_entries = glob.glob(conf_dir + "*.xml" )
  for conf_file in dir_entries:
    if os.path.isfile(conf_file):
      path, filename = os.path.split(conf_file)
      name = os.path.splitext(filename)[0]
      params = read_xml_config(filename)
      conf['configurations'][name] = params
  
  return conf
  
  
  


# Gets full path to configuration directory. Always ends with a forward slash (/)
def get_conf_dir():
  '''Gets the full path to the configuration directory. Will always end with a forward slash.
  
  Searches through the following list of locations for a directory named 'configuration'.
    - The current working directory
    - The directory of the python file
    - One level above working directory
    - Two levels above working directory
    
  Returns:
    str: path to the configuration directory.
    
  Raises:
    EnvironmentError: Raised when no configuration directory is found.
    
  '''
  dirs = [str(os.getcwd()), str(os.curdir), '../', os.path.dirname(os.path.abspath(__file__)) + '/../..']
  for loc in dirs:
    if not (str(loc).endswith('/')):
      loc += '/'
    loc += 'configuration/'
    if(os.path.exists(loc)):
      return loc
  raise EnvironmentError('Could not find conf directory')
  
  
  