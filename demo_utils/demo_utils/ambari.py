'''A module which house Ambari - an instantiable Ambari client'''
import json, time
from curl_client import CurlClient
from logs import Logger

logger = Logger('Ambari').getLogger()

class Ambari:
  
  username = password = server = port = proto = ''
  
  @staticmethod
  def load_output(output):
    '''Load the output from the curl_client into an object
    
    The idea behind this function is to try and keep the same behavior on failed requests across the entire client.
    
    Args:
      output: (str):  The output from a curl_client action
    
    Returns:
      dict: a dictionary object with a message attribute. If there was no output then the message is a string. Else there will be a nested object under 'message' which contains the returned JSON object from Ambari.
      
    Raises:
      ValueError: This is raised when a JSON object can't convert output into JSON
      '''
    json_str = ''
    if not len(output[0]) == 0:
      json_str = output[0]
    elif not len(output[1]) == 0:
      # StdErr output
      json_str = '{ "message": "" }'
      res = json.loads(json_str) # Built from json_str no chance for error (as far as can tell)
      res['message'] = output[1]
      return res
    else:
      json_str = '{ "message" : "No output was returned." }'
    
    res = ''
    
    try:
      res = json.loads(json_str)
    except ValueError as e:
      logger.error('Could not convert to JSON: ' + res)
      raise ValueError(e)
    
    return res
  
  def service_action(self, cluster_name, service_name, action):
    '''Executes an action on a given service inside of a cluster. Action must be one of START, STOP, or RESTART
    
    Args:
      cluster_name (str): the name of the cluster that the service resides in
      service_name (str): the name of the service which we are acting on
      action (str): A string of 'START', 'STOP', or 'RESTART
      
    Returns:
      bool: True is the action is completed successfully, False if otherwise.
    '''
    
    logger.info('Attempting Service Action: ' + action + '; Service Name: ' + service_name)
    if not (action == 'START' or action == 'RESTART' or action == 'STOP'):
      logger.error('Service actions was not one of START, STOP, or RESTART')
      raise ValueError('Service action must be one of: START, STOP, or RESTART')
    
    logger.info(action + 'ing ' + service_name + ' via Ambari REST API')
    
    request_payload = {}
    request_payload['RequestInfo'] = {}
    request_payload['RequestInfo']['context'] = action + ' ' + service_name + ' via REST'
    request_payload['Body'] = {}
    request_payload['Body']['ServiceInfo'] = {}
    
    service_info = self.get_service(cluster_name, service_name, 'fields=ServiceInfo')[0]
    before_state = service_info['ServiceInfo']['state']
    logger.debug('Service state before attempting to change: ' + str(before_state))
    after_state = ''
    
    if action == 'STOP':
      after_state = 'INSTALLED'
      
    elif action == 'START':
      after_state = 'STARTED'
      
    elif action == 'RESTART':
      r1 = self.service_action(service_name, cluster_name, 'STOP')
      r2 = self.service_action(service_name, cluster_name, 'START')
      return r1 and r2
    
    request_payload['Body']['ServiceInfo']['state'] = after_state
    
    payload = json.dumps(request_payload)
    res = self.client.make_request('PUT', '/api/v1/clusters/' + cluster_name + '/services/' + service_name, '-i -d \'' + payload + '\' -H "X-Requested-By:ambari"', 'fields=ServiceInfo')
    
    if not ('202 Accepted' in res[0] or '200 OK' in res[0]):
      logger.error('No 200 Level status when attempting to change service state')
      return False
    
    service_state = ''
    t = 0
    while t < self.service_wait_time:
      logger.debug('Checking for a change in service state')
      service_state = self.get_service(cluster_name, service_name, 'fields=ServiceInfo')[0]['ServiceInfo']['state']
      if service_state == after_state:
        logger.info('Service action completed successfully')
        return True
      t += 1
      time.sleep(1)
      
    return False
  
  
  def get_clusters(self, query=''):
    '''Returns a list of clusters from the given Ambari host/port. Equivalent to GET /api/v1/clusters
    
    Args:
      query (string, optional): A formatted query string which is appended to the end of the request URL (advanced). Used for filtering results.
      
    Returns:
      dict: An object which is created after being passed to self.load_output'''
    
    logger.info('Making request to /api/v1/clusters/')
    output = self.client.make_request('GET', '/api/v1/clusters', query)
    res = self.load_output(output)
    return res
  
  def get_services(self, cluster_name, query=''):
    '''Get a list of services installed on a cluster. Equivalent to GET /api/v1/clusters/{cluster_name}/services

    Args:
      cluster_name (string): The name of the cluster to query
      query (string, optional): A query to be appended to the url for filtering results

    Returns:
      dict: a dictionary object built from the HTTP response and self.load_output'''
  
    logger.info('Making request to /api/v1/clusters/' + cluster_name + '/services')
    output = self.client.make_request('GET', '/api/v1/clusters/' + cluster_name + '/services', query)
    return self.load_output(output)
  
  def get_cluster_info(self, cluster_name, query=''):
    '''Get all of the information about a current cluster. Equivalent to GET /api/v1/clusters/{cluster_name}

    Args:
      cluster_name (string): The name of the cluster to query.
    '''
  
    logger.info('Making request to /api/v1/clusters/' + cluster_name)
    output = self.client.make_request('GET', '/api/v1/clusters/' + cluster_name, query)
    return self.load_output(output)
  
  def get_service(self, cluster_name, service_name, query=''):
    logger.info('Making request to /api/v1/clusters/' + cluster_name)
    output = self.client.make_request('GET', '/api/v1/clusters/' + cluster_name + '/' + service_name, query)
    return self.load_output(output)
  
  
  def set_username(self, user):
    self.username = user
    self.client.set_username(self.username)
    
  def set_password(self, password):
    self.password = password
    self.client.set_password(self.password)
    
  def set_proto(self, proto):
    self.proto = proto
    self.client.set_proto(self.proto)
  
  def set_server(self, server):
    self.server = server
    self.client.set_server(self.server)
  
  def set_port(self, port):
    self.port = port
    self.client.set_port(self.port)
    
  def set_service_wait_time(self, wait_time):
    if wait_time > 0:
      self.service_wait_time = wait_time
    
  
  def __init__(self, username='', password='', proto='http', server='127.0.0.1', port=8080, service_wait_time=60):
    '''Initalize the client
    
    Args:
      username'''
    self.client = CurlClient()
    if service_wait_time > 0:
      self.set_service_wait_time(service_wait_time)
    else:
      self.set_service_wait_time(60)
    if not username == '':
      self.set_username(username)
      
    if not password == '':
      self.set_password(password)
      
    if not proto == '':
      self.set_proto(proto)
    
    if not server == '':
      self.set_server(server)
      
    if not len(str(port)) == 0:
      self.set_port(port)