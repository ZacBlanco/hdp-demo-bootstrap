import json, time
from curl_client import CurlClient
from logs import Logger

logger = Logger('Ambari').getLogger()

class Ambari:
	
	username = password = server = port = proto = ''
	
	@staticmethod
	def load_output(output):
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
		logger.info('Making request to /api/v1/clusters/')
		output = self.client.make_request('GET', '/api/v1/clusters', query)
		res = self.load_output(output)
		return res
	
	def get_services(self, cluster_name, query=''):
		logger.info('Making request to /api/v1/clusters/' + cluster_name + '/services')
		output = self.client.make_request('GET', '/api/v1/clusters/' + cluster_name + '/services', query)
		return self.load_output(output)
	
	def get_cluster_info(self, cluster_name, query=''):
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