# First thing to do...
# Import the demo_utils module :)
import sys, os
filedir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(filedir + '/../demo_utils')

# Use demo_utils if necessary
import demo_utils

def on_service_start():
  '''This method will run every time the service start
  
  Fill in this method with any necessary commands to set up and start other services for the demo
  
  Note that this method will always be the very last thing to be executed upon starting the demo service
  '''
  print 'Running on_service_start'
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
  
  
  
  
  
  
  
  
  
  