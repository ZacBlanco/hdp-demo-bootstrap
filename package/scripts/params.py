import sys, os, pwd, grp, signal, time, glob
#from resource_management import *
#from subprocess import call
#
## Shell of params.py
##
##
## Define variables here which you can then use in master.py
#
#config = Script.get_config()
#
#demo_port = config['configurations']['demo-config']['demo.server.port']
#ambari_user = config['configurations']['demo-config']['demo.ambari.user']
#ambari_pass = config['configurations']['demo-config']['demo.ambari.password']
#data_config = config['configurations']['demo-config']['demo.data.configuration']

demo_user = 'demo'
demo_group = 'demo'
demo_pid_dir = '/var/run/demo'
demo_pid_file = '/var/run/demo/demo.pid'
demo_log_dir = '/var/log/demo'
demo_log_file = '/var/log/demo.log'

filedir = os.path.dirname(os.path.realpath(__file__))
demo_bin_dir = filedir + '/../../demo-files'
