'''A client for executing HTTP requests via cURL. It does not use any external libraries. The only requirement is that you have the curl executable in your PATH or bin.

Used to make arbitrary http(s) requests.
'''
import json, logging
from shell import Shell
from logs import Logger

logger = Logger('CurlClient').getLogger()


class CurlClient:
  '''The CurlClient object. Houses the parameters used when making requests

  Args:
    username (str, optional): Username for basic authentication. Default empty string
    password (str, optional): Password for basic authentication. Default empty string
    proto (str, optional): protocol used in requests. Must be one of http or https
    server (str, optional): The server or hostname to which we will make the request. Defaults 127.0.0.1
    port (int, optional): The integer number of the port that the server runs on. Defaults 8080
  '''
    
  username = ''
  '''Username for basic authentication'''
  
  password = ''
  '''Password for basic authentication'''
  
  server = ''
  '''Server or hostname to connect to'''
  
  port = ''
  '''Port to connect to'''
  
  proto = ''
  '''Protocol to use when connecting via cURL'''
  
  cmd = Shell()
  
  def set_username(self, username):
    '''Set the basic authentication username
    
    Args:
      username (str)
      
    Returns:
      N/A
      '''
    self.username = username
  
  def set_password(self, password):
    '''Set the basic authentication password
    
    Args:
      password (str)
      
    Returns:
      N/A
      '''
    self.password = password
  
  # Set HTTP protocol (http or https)
  def set_proto(self, proto):
    '''Set the protocol. Must be http or https
    
    Args:
      proto (str)
      
    Returns:
      N/A
      
    Raises:
      ValueError: When proto argument is not one of http or https
      '''
    if proto == 'http' or proto == 'https':
      self.proto = proto
    else:
      logger.error('protocol was not one of \'http\' or \'https\'')
      raise ValueError('Protocol must be http or https')
  
  def set_server(self, server):
    '''Set the server to connect to
    
    Args:
      server (str)
      
    Returns:
      N/A
      '''
    self.server = server
  
  # A number between 0 and 65535 
  def set_port(self, port):
    '''Set the port to connect to
    
    Args:
      port (int, str)
      
    Returns:
      N/A
      
    Raises:
      ValueError: When the port argument can't be converted to an int. Or when the port is less than 0 or greater than 65535
      '''
    int_port = -1
    try:
      int_port = int(port)
    except ValueError as e:
      logger.error('Port could not be converted to int')
      raise ValueError('Server port was not of type: int')
    
    if int_port > 0 and int_port <= 65535:
      self.port = int_port
    else:
      logger.error('Port was out of range')
      raise ValueError('Server port must be between 0 and 65535. Value was ' + str(port))
  
  
  # Make a request via cURL
  # Must pass an HTTP verb GET|PUT|POST|DELETE
  # The request to the server (possibly something like /api/v1/resource...)
  # A list of query parameters
  #   ['param1=value1', 'param2=value2']
  
  def make_request(self, verb, request, options='', query=''):
    '''Make the actual request using cURL and the demo_utils.shell module.
    
    Args:
      verb (str): the HTTP verb to use. Currently only supporting GET/PUT/POST/DELETE
      request (str): The request path. Simply appended to the end of PROTO://HOST:PORT. Should begin with a leading '/'.
      options (str, optional): cURL command line argument that you which to be included. This might include headers or more.
      query (str, optional): The query string to be appended to the end of the request URL.
      
    Returns:
      list: A two item list. The [0] element is the output to stdout. The [1] element is the curl output to stderr
      
    Raises:
      ValueError: When the HTTP verb is not one of GET/PUT/POST/DELETE
      
      '''
    
    if not (verb == 'GET' or verb == 'POST' or verb == 'PUT' or verb == 'DELETE'):
      raise ValueError('HTTP Verb must be one of GET|PUT|POST|DELETE')
    
    url = ''.join([self.proto, '://', self.server, ':', str(self.port), request])
    url = url + '?'
    url = url + query
    logger.debug('REQUEST URL: ' + url)
    
    credentials = ':'.join([self.username, self.password])
    credentials = '-u ' + credentials
    
    method = '-X ' + verb
    
    call = ' '.join(['curl -sS', credentials, method, options, url])
    logger.info('CURL CALL: ' + call)
    output = self.cmd.run(call)
    logger.debug('CURL STD OUT: ' + output[0])
    logger.debug('CURL STD ERR: ' + output[1])
    return output
    
  
  def __init__(self, username='', password='', proto='http', server='127.0.0.1', port=8080):
    '''The CurlClient object. Houses the parameters used when making requests
    
    Args:
      username (str, optional): Username for basic authentication. Default empty string
      password (str, optional): Password for basic authentication. Default empty string
      proto (str, optional): protocol used in requests. Must be one of http or https
      server (str, optional): The server or hostname to which we will make the request. Defaults 127.0.0.1
      port (int, optional): The integer number of the port that the server runs on. Defaults 8080
    '''
    self.set_username(username)
    self.set_password(password)
    self.set_server(server)
    self.set_port(port)
    self.set_proto(proto)



















