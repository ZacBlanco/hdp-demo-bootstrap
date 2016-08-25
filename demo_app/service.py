# First thing to do...
# Import the demo_utils module :)
import sys, os
filedir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(filedir + '/../demo_utils')

# Use demo_utils if necessary
import demo_utils, logging
from demo_utils import config, ambari
from demo_utils.ambari import Ambari
from demo_utils import service_installer
from demo_utils import logs

rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)
log = logs.Logger('SERVICE.py').getLogger()

def on_service_start():
  '''This method will run every time the service start
  
  Fill in this method with any necessary commands to set up and start other services for the demo
  
  Note that this method will always be the very last thing to be executed upon starting the demo service
  '''
  print 'Running on_service_start'
  cfg = config.read_config('global.conf')
  
  # Ambari Client
  amc = Ambari(config=cfg['AMBARI'])
  
  #Queue  Services
  amc.service_action('Sandbox', 'KAFKA', 'START', queue=True)
  amc.service_action('Sandbox', 'ZEPPELIN', 'START', queue=True)
  try:
    # Not guaranteed to be installed
    amc.service_action('Sandbox', 'NIFI', 'START', queue=True)
  except:
    log.warn('Failed to start NiFi')
  
  service_installer.add_zeppelin_notebooks()
  # Add anything else below that might be necessary for when the demo starts
  
  
  
  
  pass

def on_service_stop():
  '''This method will run every time the service stops
  
  Fill in this method with any necessary commands to clean up or stop other services from the demo
  
  Note that this method will always be the very last thing to be executed upon stopping the demo service.
  '''
  print 'Running on_service_stop'
  pass

def on_service_install():
  '''This method will run only once - when the service is installed through Ambari.
  
  Fill in this method with any necessary one-time commands to set up the environment before starting the demo.
  
  Note this method will only be run **after** the demo has run its setup commands. This method will always be the last thing to be run before starting the service.
  '''
  print 'Running on_service_install'
  
#  service_installer.install_nifi()
  service_installer.add_zeppelin_notebooks()
  service_installer.add_nifi_templates()
  
  
  
  
  pass

if __name__ == "__main__":
  args = sys.argv[1:]
  if len(args) >= 1:
    cmd = args[0].lower()
    if 'install' == cmd:
      on_service_install()
    elif 'start' == cmd:
      on_service_start()
    elif 'stop' == cmd:
      on_service_stop()
  else:
    print 'Could not run service commands. Arguments not specified correctly'
  
  
  
  
  
  
  