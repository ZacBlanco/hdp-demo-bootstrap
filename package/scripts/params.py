import sys, os, pwd, grp, signal, time, glob
from resource_management import *
from resource_management.core import shell
from subprocess import call

# Shell of params.py
#
#
# Define variables here which you can then use in master.py

config = Script.get_config()

demo_user = 'demo'
demo_group = 'demo'
demo_pid_dir = '/var/run/demo'
demo_pid_file = '/var/run/demo/demo.pid'
demo_log_dir = '/var/log/demo'
demo_log_file = '/var/log/demo.log'

demo_conf_pull_url = config['configurations']['demo-config']['demo.conf.pull_url']

# Installation Directory
demo_conf_install_dir = 'missing_dir'

demo_conf_install_dir = shell._call('find /var/lib/ambari-server/ -name DEMOSERVICE')[1]

print(demo_conf_install_dir)

if demo_conf_install_dir == 'missing_dir':
  raise ValueError('Could not find the DEMOSERVICE directory.')

if not demo_conf_install_dir.endswith('/'):
  demo_conf_install_dir = demo_conf_install_dir + '/'

demo_bin_dir = demo_conf_install_dir + 'demo_app'
demo_conf_dir = demo_conf_install_dir + 'configuration'

# Demo Section
demo_server_port = config['configurations']['demo-config']['demo.server.port']

demo_data_bytes_per_second = config['configurations']['demo-config']['demo.data.bytes_per_second']
demo_data_configuration = config['configurations']['demo-config']['demo.data.configuration']
demo_data_write_file_location = config['configurations']['demo-config']['demo.data.write_file_location']
demo_data_kafka_listener = config['configurations']['demo-config']['demo.data.kafka_listener']
demo_data_http_endpoint = config['configurations']['demo-config']['demo.data.http_endpoint']
demo_zk_connection = config['configurations']['demo-config']['demo.zk_connection']
demo_kafka_topics_script = config['configurations']['demo-config']['demo.kafka_topics_script']
demo_kafka_topic_name = config['configurations']['demo-config']['demo.kafka_topic_name']



# Ambari Section
demo_ambari_username = config['configurations']['demo-config']['demo.ambari.username']
demo_ambari_password = config['configurations']['demo-config']['demo.ambari.password']
demo_ambari_server = config['configurations']['demo-config']['demo.ambari.server']
demo_ambari_port = config['configurations']['demo-config']['demo.ambari.port']
demo_ambari_cluster_name = config['configurations']['demo-config']['demo.ambari.cluster_name']
demo_ambari_proto = config['configurations']['demo-config']['demo.ambari.proto']


# Zeppelin Section
demo_zeppelin_notebooks_directory = config['configurations']['demo-config']['demo.zeppelin.notebooks_directory']

# NiFi Section
demo_nifi_install_dir = config['configurations']['demo-config']['demo.nifi.install_dir']

# Logging
demo_logging_log_level = config['configurations']['demo-config']['demo.logging.log_level']

# Configuration Template
demo_global_conf_template = config['configurations']['demo-config']['demo.global.conf']
