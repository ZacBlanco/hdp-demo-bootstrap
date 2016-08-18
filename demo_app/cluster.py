'''This file houses utility functions for interacting with the cluster and portions of the web application. Namely the Websockets server and Echo app implementation reside here.


'''
# First thing to do...
# Import the demo_utils module :)
import sys, os
filedir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(filedir + '/../demo_utils')

import threading, kafka, requests, time, json

from kafka import KafkaProducer
from demo_utils.curl_client import CurlClient
from demo_utils.shell import Shell
from demo_utils.ambari import Ambari
from demo_utils import config, generator, logs
from gevent import monkey; monkey.patch_all()
from ws4py.websocket import WebSocket
from ws4py.server.geventserver import WSGIServer, WebSocketWSGIHandler, WSGIServer
from ws4py.server.wsgiutils import WebSocketWSGIApplication


HIVE_TYPE_MAP = {
  "int": "INT",
  "decimal": "DOUBLE",
  "string": "STRING",
  "boolean": "BOOLEAN",
  "map": "STRING" # This will change in the future - possibly add mapType?
}
'''Maps types from datum types to Hive types'''


SPARK_TYPE_MAP = {
  "int": "Int",
  "decimal": "Double",
  "string": "String",
  "boolean": "Boolean",
  "map": "String" # This will change in the future - possibly add mapType?
}
'''Maps types from datum types to Scala types'''

logger = logs.Logger('CLUSTER.py').getLogger()

def kerberize():
  '''Kerberize the cluster using a script. Untested. Can take 10-15 minutes.
  
  This utilizes a script found at https://github.com/crazyadmins/useful-scripts/tree/master/ambari
  
  If you're running this script on a cluster you should look in ``configuration/kerberos/ambari.props`` to make sure the proper values are present in the file or else the script will fail.
  
  Args:
    N/A
    
  Returns:
    N/A
  '''
  script = config.get_path('kerberos/setup_kerberos.sh')
  sh = Shell()
  sh.run('bash ' + script)
  
def create_demo_kafka_topic():
  '''Creates a kafka topic for the demo if it doesn't already exist.
  
  The caveat here in using this is that Kafka must be installed on the same machine as the demo, and thus the same machine as Ambari as well. The function will try to start the Kafka service through Ambari and then once the service is started is will use the location of the Kafka topics script to create the topic
  
  The name for the topic is specified in ``global.conf``.
  
  
  Args:
    N/A
    
  Returns:
    bool: True if the creation is successful. False otherwise.
  '''
  conf = config.read_config('global.conf')
  am_conf = conf['AMBARI']
  amc = Ambari(am_conf['username'], am_conf['password'], am_conf['proto'], am_conf['server'], am_conf['port']);
  
  logger.info('Starting Kafka Broker')
  
  if amc.service_action('Sandbox', 'KAFKA', 'START'):
    sh = Shell()
    topics_script = conf['DEMO']['kafka_topics_script']
    zk = conf['DEMO']['zk_connection']
    topic_name = conf['DEMO']['kafka_topic_name']
    logger.info('Attempting to create new Kafka Topic')
    out = sh.run(topics_script + ' --create --zookeeper ' + zk + ' --replication-factor 1 --partitions 1 --topic ' + topic_name)
    logger.debug(str(out))
    if len(out[1]) == 0:
      return True
    else:
      return False
  
def get_kafka_topics():
  '''List the kafka topics on the current installation.
  
  Requires that Kafka is installed on the same machine and Ambari is up and running. Will start the service and use the Kafka scripts to list out all of the topics.
  
  
  Args:
    N/A
    
  Returns:
    list: [0] will contain the list of all the topics in a string, typically separated by newlines. [1] will contain any errors when retrieving the topics.
  
  '''
  conf = config.read_config('global.conf')
  am_conf = conf['AMBARI']
  amc = Ambari(am_conf['username'], am_conf['password'], am_conf['proto'], am_conf['server'], am_conf['port']);
  
  logger.info('Starting Kafka Broker')
  
  if amc.service_action('Sandbox', 'KAFKA', 'START'):
    sh = Shell()
    topics_script = conf['DEMO']['kafka_topics_script']
    zk = conf['DEMO']['zk_connection']
    logger.info('Attempting to create new Kafka Topic')
    out = sh.run(topics_script + ' --list --zookeeper ' + zk)
    
    if len(out[1]) == 0:
      topics = out[0]
      topics = topics.strip().split('\n')
      logger.info('Kafka topics output: ' + str(topics))
      return topics
    
  return ['', 'Unable to get topics. Could not start Kafka Broker']

def generate_queries(schema, table_name='demo_table'):
  '''Generate test queries based on a configuration for the data generator
  
  Currently supported components:
  
  - Spark
  - Hive
  
  Sample JSON Return:
  
  ..code-block:: json
  
    {
      'HIVE': [
        {
          'name': '{CODE}',
          'name2: '{CODE2}',
          'name3': '{CODE3}',
          'name4: '{CODE4}',
        }
      ],
      'SPARK': [
        {
          'name': '{CODE}'
        }
      ]
    }
  
  Args:
    schema (str): The schema for the generator as a JSON string
    
  Returns:
    dict: An object that holds keys for different objects, where each key points to a list of strings (queries) for various components.
  '''
  logger.info('Building queries')
  fields = json.loads(schema)
  conf = config.read_config('global.conf')['DEMO']
  hdfs_file_path = conf['data_write_hdfs_file_location']
  
  hdfs_data_dir = os.path.dirname(hdfs_file_path)
  
  table_name = 'demo_table'
  queries = {}
  # Build a hive query to insert into a table
  hive_queries = {
    'Basic Table': 'CREATE TABLE IF NOT EXISTS ' + table_name,
    'External Table': 'CREATE EXTERNAL TABLE IF NOT EXISTS ' + table_name,
    'Drop Table': 'DROP TABLE ' + table_name,
    'HDFS CSV': 'CREATE EXTERNAL TABLE IF NOT EXISTS ' + table_name,
  }
  basic_create = 'CREATE TABLE IF NOT EXISTS ' + table_name
  external_create = 'CREATE EXTERNAL TABLE IF NOT EXISTS ' + table_name
  drop_table = 'DROP TABLE ' + table_name
  
  cols = map(lambda d: [str(d['fieldName']), str(HIVE_TYPE_MAP[d['type']])], fields)
  ftypes = sorted(map(lambda c: ' '.join(c), cols))
  field_set = ' (' + ', '.join(ftypes) + ')'
  
  hive_queries['Basic Table'] += field_set
  hive_queries['External Table'] += field_set + ' LOCATION \'' + hdfs_data_dir + '\''
  hive_queries['HDFS CSV'] += field_set + '\nROW FORMAT\nDELIMITED FIELDS TERMINATED BY \', \'\nSTORED AS TEXTFILE\nLOCATION \'' + hdfs_data_dir + '\''
  queries['HIVE'] = hive_queries
  
  spark_queries = {
    'RDD and Temporary DataFrame': "",
    'SparkSQL - Select all': ''
  }
  # Build class
  rdd_temp = ''
  class_name = "Data"
  cols = map(lambda d: [str(d['fieldName']), str(SPARK_TYPE_MAP[d['type']])], fields)
  ftypes = sorted(map(lambda c: ': '.join(c), cols))
  field_set = '(' + ', '.join(ftypes) + ');'
  rdd_temp += "case class " + class_name + field_set + '\n'
  rdd_temp += 'val csv = sc.textFile("hdfs:' + hdfs_file_path + '");\n'
  rdd_temp += 'val data = csv.map(line => line.split(",").map(e => e.trim));\n'
  lambda_arg = 'a'
  class_args = []
  sort_cols = sorted(cols)
  for i in range(len(cols)):
    # Build the class constructor for the map function
    s = lambda_arg + '(' + str(i) + ').to' + str(sort_cols[i][1])
    class_args.append(s)
  
  lambda_func = lambda_arg + ' => ' + class_name + '(' + ', '.join(class_args) + ')'
  rdd_temp += 'val df = data.map(' + lambda_func + ').toDF();\n'
  rdd_temp += 'df.registerTempTable("' + table_name + '");'
  
  spark_queries['RDD and Temporary DataFrame'] = rdd_temp
  spark_queries['SparkSQL - Select all'] = 'SELECT * FROM ' + table_name
  
  queries['SPARK'] = spark_queries
  
  
  return queries
  


class ThreadedGenerator(threading.Thread):
  '''A generator which runs on a separate thread when generating data.
  
  This thread will generate data indefinitely unless the program is killed or ``self.stop()`` is called.
  
  Args:
    schema (str): The json schema for the data generator (a file or json string)
    bps (int): The number of bytes of data to produce each second.
    outputs (list): A list containing any any of the following:
    
      - ``'KAFKA'``
      - ``'FILE'``
      - ``'HTTP'``
      - ``'HDFS'``
      
      This determines the locations where data is sent after it is generated. If the string is present then the data will be sent to the specified location. Values other than these are ignored.
  '''
  def __init__(self, schema, bps, outputs, data_pool_size=100):
    threading.Thread.__init__(self)
    self.outputs = outputs
    self.daemon = True
    self.flag = True
    self.data_pool_size = data_pool_size
    self.http_data_pool = []
    self.hdfs_data_pool = []
    if bps > 0:
      self.bps = bps
    else:
      self.bps = 50000 #50kb
    self.gen = generator.DataGenerator(schema)
    
    conf = config.read_config('global.conf')['DEMO']
    self.exports = {}
    if 'KAFKA' in outputs:
      self.kafka_topic = conf['kafka_topic_name']
      self.kafka_listener = conf['data_kafka_listener']
      has_topic = False
      if not (self.kafka_topic in get_kafka_topics()[0]):
        topic_created = create_demo_kafka_topic()
        if topic_created:
          has_topic = True
        else:
          raise EnvironmentError('Could not create Kafka Topic')
          
      else:
        has_topic = True
      
      if has_topic:
        self.exports['KAFKA'] = True
        self.kafka_producer = KafkaProducer(bootstrap_servers=self.kafka_listener)
      else:
        self.exports['KAFKA'] = False
        msg = 'Could not create Kafka Topic. Please create manually'
        raise EnvironmentError(msg)
        logger.warn(msg)
    else:
      self.exports['KAFKA'] = False
    
    if 'FILE' in outputs:
      self.export_filename = conf['data_write_file_location']
      self.exports['FILE'] = True
      with open(self.export_filename, 'w') as ex_data:
        pass
    else:
      self.exports['FILE'] = False
      
    if 'HDFS' in outputs:
      self.export_hdfs_file = conf['data_write_hdfs_file_location']
      self.exports['HDFS'] = True
    else:
      self.exports['HDFS'] = False
    
    if 'HTTP' in outputs:
      self.export_http_url = conf['data_http_endpoint']
      self.exports['HTTP'] = True
    else:
      self.exports['HTTP'] = False
  
  def export_kafka(self, data):
    '''Export a message to Kafka
    
    This function utlizes the kafka-python library It also reads in the broker URL and topic name from ``global.conf``
    
    Args:
      data (dict/object): An object to encode from the generator to send to Kafka.
    
    Returns:
      N/A
    '''
    self.kafka_producer.send(self.kafka_topic, json.dumps(data).encode('utf-8'))
  
  def export_file(self, data):
    '''Write out data from the generator to a file **in CSV format**
    
    The file to write to is found in ``global.conf``. Header lines are not written to the file. All data is appended to a single file. There is no rotation.
    
    When a new data generator starts the file is essentially 'wiped out' so make sure to copy the data elsewhere before stopping/restarting the generator.
    
    Args:
      data (dict/object): The data from the generator here writes out the data as a CSV for easier ingestion into other places like Hive or Spark.
    
    Returns:
      N/A
    
    '''
    with open(self.export_filename, 'a') as ex_data:
      line = ', '.join(map(lambda v: str(data[v]), data.keys())) + '\n'
      ex_data.write(line)
    
  def export_hdfs(self, data):
    '''Write out data from the generator to a file **in CSV format in HDFS**
    
    The file to write to is found in ``global.conf``. Header lines are not written to the file. All data is appended to a single file.
    
    When a new data generator starts the file is essentially 'wiped out' so make sure to copy the data elsewhere before stopping/restarting the generator.
    
    Args:
      data (dict/object): The data from the generator here writes out the data as a CSV for easier ingestion into other places like Hive or Spark.
    
    Returns:
      N/A
    
    '''
    
    self.hdfs_data_pool.append(data)
    if len(self.hdfs_data_pool) > self.data_pool_size:
      header = ', '.join(map(lambda v: v, sorted(self.hdfs_data_pool[0].keys())))
      lines = '\n'.join(map(lambda v: ', '.join(map( lambda k: str(v[k]), sorted(v.keys()))), self.hdfs_data_pool))
      lines = lines.replace('\"', '"') # Unescape to make sure all quotes are unescaped first
      lines = lines.replace('"', '\"') # Escape so bash command doesn't fail if we have quotes included.
      self.hdfs_data_pool = []
      hdfs_file = self.export_hdfs_file
      bash = Shell();
      hdfs_cmd = 'hdfs dfs -appendToFile - ' + hdfs_file
      echo_cmd = 'echo "%s"' % (lines)
      cmd = ' | '.join([echo_cmd, hdfs_cmd])
      output = bash.run(cmd)
      logger.debug('HDFS Append Output: ' + str(output))
      
    
    
  def export_http(self, data):
    '''Export data and POST to an Http endpoint.
    
    Data is 'pooled' before being sent in order to save resources and overhead on requests. The default pool value is 1000 records. This means for every 1000 pieces of data, one request will be made. The data is stored as JSON in the body of the request.
    
    The caveat here is that if you stop the data generator the remaining data in the pool will not be sent.
    
    Args:
      data (dict/object): A piece of data to POST. If the data is still below the pool size we add the data in to the data 'pool' and wait for more data to come in. When the threshold is reached a request with all of the data is sent.
      
    Returns:
      N/A
    '''
    if len(self.http_data_pool) >= self.data_pool_size:
      logger.info('POSTing Data Pool')
      logger.info('Data Pool Size: ' + str(len(self.http_data_pool)))
      requests.post(self.export_http_url, json=self.http_data_pool)
      self.http_data_pool = []
      
      
  def run(self):
    '''Run method for the thread implementation. Runs until the thread is killed.
    
    Args:
      N/A
    '''
    while self.flag:
      bytes = 0
      lines = 0
      start = time.time()
      # generate all the data and do something with it
      while bytes <= self.bps:
        data = self.gen.generate()
        bits = len(json.dumps(data).encode('utf-8'))
        bytes = bytes + bits
        # Now export the data somewhere.....
        if self.exports['FILE']:
          self.export_file(data)
        if self.exports['KAFKA']:
          self.export_kafka(data)
        if self.exports['HTTP']:
          self.export_http(data)
        if self.exports['HDFS']:
          self.export_hdfs(data)
      # sleep until the next second once we've generated enough data
      while (time.time() - start <= 1):
        time.sleep(0.1)

  def stop(self):
    '''Stops the generator by setting the flag to ``False``. This causes the ``run`` method to exit and the thread to finish.
    
    Args:
      N/A
    
    '''
    self.flag = False


class WSEcho(WebSocket):
  '''The WebSocket handler for the WebSocket application
  
  This class defines three methods required for the websocket server.
  
  The three methods are 
  
  - opened
  - closed
  - received_message
  
  '''
  app_name = 'WebsocketApplication'
  def opened(self):
    '''Defines behavior for when a new client connects to the server
    
    In this case we add the client to our list of clients so we know who we can send messages too.
    
    The clients are accessed through ``environ``.
    '''
    self.log = logs.Logger(WSEcho.app_name).getLogger()
    app = self.environ['ws4py.app']
    if not self in app.clients:
      app.clients.append(self)
      self.log.info('websocket app: client connected')
    
    self.log.debug('opened - Clients: ' + str(app.clients))
  
  def closed(self, code, reason=None):
    '''Defines behavior for when a client disconnects from the websocket server
    
    In this case when a client disconnects we check and remove them from the client list.
    '''
    self.log = logs.Logger(WSEcho.app_name).getLogger()
    app = self.environ.pop('ws4py.app')
    
    if self in app.clients:
      self.log.info('websocket app: client disconnected')
      app.clients.remove(self)
    
    self.log.debug('closed - Clients: ' + str(app.clients))
  
  def received_message(self, message):
    '''Defines behavior for when a client sends a message to the server
    
    In this case we don't expect the clients to send us data so we just log the message.
    '''
    self.log = logs.Logger(WSEcho.app_name).getLogger()
    self.log.info('websocket app: Message: ' + str(message))
    


class WSDemoApp(object):
  '''This is the Websocket Demo Application. 
  
  Here we define the initialization of the server. We also determine how to handle a request to the websocket server. In this case we don't have different routes on the websocket server other than the root path ``/``.
  
  Here we also define other functions such as ``broadcast`` for when we want to send clients information
  
  Args:
    N/A
    
  Returns:
    N/A
  '''
  
  def __init__(self):
    self.log = logs.Logger('WebSocketHandler').getLogger()
    self.log.info('InitWebsocket app')
    self.ws = WebSocketWSGIApplication(handler_cls=WSEcho)
    self.clients = []
  
  def __call__(self, environ, start_response):
    '''Defines behavior when a new request is received
    
    We ignore any requests to anything that isn't the root path ``/`` and initiate the response handling in here.
    
    This method shouldn't be modified unless you know what you're doing.
    
    '''
    if environ['PATH_INFO'] == '/':
      environ['ws4py.app'] = self
      self.ws(environ, start_response)
    else:
      self.log.info('Client requested non-root path. Not handling request.')
    
  def broadcast(self, message):
    '''Broadcast a message to all server clients.
    
    Args:
      message (str): The string to broadcast to every client
      
    Returns:
      N/A
      
      '''
    for client in self.clients:
      try:
        client.send(message)
      except:
        self.log.info('Error sending message to client: ' + client)
        pass
    
    
    
class WSDemoServer(threading.Thread):
  '''A threaded wrapper around the websockets server so that we can run the Flask and Websockets in parallel together.
  
  Args:
    port (int): The port number for the Websockets server to run on.
    
  '''
  
  def __init__(self, host, port):
    threading.Thread.__init__(self)
    self.log = logs.Logger('WebSocketsServer').getLogger()
    self.port = int(port)
    self.host = host
    self.daemon = True
    self.flag = True
    self.server = WSGIServer((self.host, self.port), WSDemoApp())
    pass
  
  def run(self):
    '''Runs the threaded server
    
    Args:
      N/A
      
    Returns:
      N/A
      
    '''
    self.log.info('Starting websockets server')
    self.server.serve_forever()
    
  def broadcast(self, data):
    '''A wrapper on the server's broadcast method so that it can be easily accessed from the flask application
    
    Args:
      data (str): A string message to send to the client.
      
    Returns:
      N/A
    '''
    self.server.application.broadcast(data)
  
  def stop(self):
    '''Stops the websockets server'''
    self.server.stop()
    
    
    
    
    