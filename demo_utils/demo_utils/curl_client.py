import json, logging
from shell import Shell
from logs import Logger

logger = Logger('CurlClient').getLogger()


class CurlClient:
	username = ''
	password = ''
	server = ''
	port = ''
	proto = ''
	cmd = Shell()
	
	def set_username(self, username):
		self.username = username
	
	def set_password(self, password):
		self.password = password
	
	# Set HTTP protocol (http or https)
	def set_proto(self, proto):
		if proto == 'http' or proto == 'https':
			self.proto = proto
		else:
			logger.error('protocol was not one of \'http\' or \'https\'')
			raise ValueError('Protocol must be http or https')
	
	def set_server(self, server):
		self.server = server
	
	# A number between 0 and 65535 
	def set_port(self, port):
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
	# 	['param1=value1', 'param2=value2']
	
	def make_request(self, verb, request, options='', query=''):
		
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
		self.set_username(username)
		self.set_password(password)
		self.set_server(server)
		self.set_port(port)
		self.set_proto(proto)



















