# First thing to do...
# Import the demo_utils module :)
import sys, os
filedir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(filedir + '/../demo_utils')


def on_service_start():
  print 'on start'
  pass

def on_service_stop():
  print 'on stop'
  pass

def on_service_install():
  print 'on install'
  pass

if __name__ == "__main__":
  on_service_install()