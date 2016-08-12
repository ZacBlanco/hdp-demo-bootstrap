'''A small submodule which makes logging easy for the whole library

Using this library you can initiate logging for any module in this package (or any python module in general)

Example:
  .. code-block:: python
    :linenos:
    
    from demo_utils import logs
    from logs import Logger
    
    # Create the logger. Should be at the beginning of the file.
    # Use throughout the module/file
    l = Logger('your_logger_name').getLogger()
    
    # Info
    l.info('Info Message')
    # Warn
    l.warn('Warning Message')
    # Error
    l.error('Error Message')
    # Debug
    l.debug('Debug Message')
    

To set the logging level put a file called ``global.conf`` inside of your configuration directory. Use the following format to set the log level. If the file isn't found we default to WARN.

Put the following inside ``global.conf`` to set the logging level

::

  [LOGGING]
  log-level=WARN

'''
import logging, config, sys, os

class Logger():
  '''Simple logger object to set up logging for a module
  
  Args:
    name (str): The name of the module/logger. Used in log output'''
  
  logger = logging.getLogger('init')
  '''The logger object. Uses the built-in python logger.'''
  
  def getLoggingLevel(self):
    '''Attempts to retrieve the logging level from the configuration file ``global.conf``.
    
    '''
    try:
      conf = config.read_config('global.conf')['LOGGING']
      level = conf['log-level']
      if 'DEBUG' == level:
        return logging.DEBUG
      elif 'INFO' == level:
        return logging.INFO
      elif 'WARN' == level:
        return logging.WARN
      elif 'ERROR' == level:
        return logging.ERROR
      elif 'CRITICAL' == level:
        return logging.CRITICAL
      else:
        return logging.WARN
    except:
      return logging.WARN
  
  def getLogger(self):
    '''Get the logger object
    
    Returns:
      object: The python logger object'''
    return self.logger
  
  def getLogFile(self):
    '''Attempts to retrieve the log-file parameter from global.conf'''
    
    try:
      conf = config.read_config('global.conf')['LOGGING']
      log_file = conf['log-file']
      return log_file
    except:
      return ''
    
  
  def __init__(self, name):
    self.logger = logging.getLogger(name)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(self.getLoggingLevel())
    sh.setFormatter(logging.Formatter('[%(levelname)s] | %(name)s | %(message)s'))
    self.logger.addHandler(sh)
    log_file = self.getLogFile()
    if len(log_file) > 0:
      log_dir = os.path.dirname(os.path.realpath(log_file))
      try:
        if not os.path.exists(log_dir):
          os.makedirs(log_dir)
        
        fh = logging.FileHandler(log_file)
        fh.setLevel(self.getLoggingLevel())
        fh.setFormatter(logging.Formatter('[%(levelname)s] | %(name)s | %(message)s'))
        self.logger.addHandler(fh)
      except OSError as e:
          pass
