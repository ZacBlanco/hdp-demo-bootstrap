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
#from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from gevent import monkey; monkey.patch_all()
from ws4py.websocket import WebSocket
from ws4py.server.geventserver import WSGIServer, WebSocketWSGIHandler, WSGIServer
from ws4py.server.wsgiutils import WebSocketWSGIApplication



logger = logs.Logger('CLUSTER.py').getLogger()

def kerberize():
  script = config.get_path('kerberos/setup_kerberos.sh')
  sh = Shell()
  sh.run('bash ' + script)
  
def create_demo_kafka_topic():
  conf = config.read_config('global.conf')
  am_conf = conf['AMBARI']
  amc = Ambari(am_conf['username'], am_conf['password'], am_conf['proto'], am_conf['server'], am_conf['port']);
  
  logger.info('Starting Kafka Broker')
  
  if amc.service_action('Sandbox', 'KAFKA', 'START'):
    sh = Shell()
    topics_script = conf['DEMO']['kafka_topics_script']
    zk = conf['DEMO']['zk_connection']
    topic_name = conf['DEMO']['topic_name']
    logger.info('Attempting to create new Kafka Topic')
    out = sh.run(topics_script + ' --create --zookeeper ' + zk + ' --replication-factor 1 --partitions 1 --topic ' + topic_name)
    
    if len(out[1]) == 0:
      return True
    else:
      return False
  
def get_kafka_topics():
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
    
    return out
  
  return ['', 'Could not get start Kafka Broker']


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
      
      This determines the locations where data is sent after it is generated. If the string is present then the data will be sent to the specified location. Values other than these are ignored.
  '''
  def __init__(self, schema, bps, outputs, http_data_pool_size=1000):
    threading.Thread.__init__(self)
    self.outputs = outputs
    self.daemon = True
    self.flag = True
    self.http_data_pool_size = http_data_pool_size
    self.http_data_pool = []
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
    
    if 'HTTP' in outputs:
      self.export_http_url = conf['data_http_endpoint']
      self.exports['HTTP'] = True
    else:
      self.exports['HTTP'] = False
  
  def export_kafka(self, data):
    self.kafka_producer.send(self.kafka_topic, json.dumps(data).encode('utf-8'))
  
  def export_file(self, data):
    with open(self.export_filename, 'a') as ex_data:
      line = ', '.join(map(lambda v: str(data[v]), data.keys())) + '\n'
      ex_data.write(line)
    
  def export_http(self, data):
    if len(self.http_data_pool) >= self.http_data_pool_size:
      logger.info('POSTing Data Pool')
      logger.info('Data Pool Size: ' + str(len(self.http_data_pool)))
      requests.post(self.export_http_url, json=self.http_data_pool)
      self.http_data_pool = []
    else:
#      logger.debug('Appending data to data_pool')
      self.http_data_pool.append(data)
  
  def run(self):
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
      # sleep until the next second once we've generated enough data
      while (time.time() - start <= 1):
        time.sleep(0.1)

  def stop(self):
    self.flag = False


class WSEcho(WebSocket):
  app_name = 'WebsocketApplication'
  def opened(self):
    self.log = logs.Logger(WSEcho.app_name).getLogger()
    app = self.environ['ws4py.app']
    app.clients.append(self)
    
    self.log.info('SELF:' + str(self))
    self.log.info('websocket app clients: ' + str(app.clients))
    self.log.info('websocket app: client connected')
    pass
  
  def closed(self, code, reason=None):
    self.log = logs.Logger(WSEcho.app_name).getLogger()
    app = self.environ.pop('ws4py.app')
    
    if self in app.clients:
      self.log.info('websocket app clients: ' + str(app))
      app.clients.remove(self)
      
    
    self.log.info('websocket app: connection closed')
    self.log.debug(str(reason))
    pass
  
  def received_message(self, message):
    self.log = logs.Logger(WSEcho.app_name).getLogger()
    self.log.info('websocket app: received message')
    self.log.debug(str(message))
    
  def broadcast(self, message):
    self.log = logs.Logger(WSEcho.app_name).getLogger()
    for client in self.ws.handler.server.clients.values():
      pass


class WSDemoApp(object):
  
  def __init__(self):
    self.log = logs.Logger('WebSocketHandler').getLogger()
    self.log.info('InitWebsocket app')
    self.ws = WebSocketWSGIApplication(handler_cls=WSEcho)
    self.clients = []
  
  def __call__(self, environ, start_response):
    if environ['PATH_INFO'] == '/':
      environ['ws4py.app'] = self
      return self.ws(environ, start_response)
    
  def broadcast(self, message):
    for client in self.clients:
      try:
        client.send(message)
      except:
        self.log('Error sending message to client: ' + client)
        pass
    
    
    
class WSDemoServer(threading.Thread):
  
  def __init__(self, port):
    threading.Thread.__init__(self)
    self.log = logs.Logger('WebSocketsServer').getLogger()
    self.port = int(port)
    self.daemon = True
    self.flag = True
    self.server = WSGIServer(('', self.port), WSDemoApp())
    pass
  
  def run(self):
    self.log.info('Starting websockets server')
    self.server.serve_forever()
    
  def broadcast(self, data):
    self.server.application.broadcast(data)
  
  def stop(self):
    self.server.stop()
    
    
    
    
    