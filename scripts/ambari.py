import json
from curl_client import CurlClient


class Ambari:
	
	client = CurlClient()
	username = password = server = port = proto = ''
	
	@staticmethod
	def load_output(output):
		json_str = ''
		if not len(output[0]) == 0:
			json_str = output[0]
		elif not len(output[1]) == 0:
			# StdErr output
			json_str = '{ "message": "" }'
			try:
				res = json.loads(json_str)
				res['message'] = output[1]
				return res
			except ValueError as e:
				raise ValueError(e)

		else:
			json_str = '{ "message" : "No output was returned." }'
		
		res = ''
		
		try:
			res = json.loads(json_str)
		except ValueError as e:
			raise ValueError(e)
		
		return res
	
	def getClusters(self, query=''):
		output = self.client.make_request('GET', '/api/v1/clusters', query)
		res = self.load_output(output)
		return res
	
	def getServices(self, cluster_name, query=''):
		output = self.client.make_request('GET', '/api/v1/clusters/' + cluster_name + '/services', query)
		res = self.load_output(output)
		return res
	
	def getClusterInfo(self, cluster_name, query=''):
		output = self.client.make_request('GET', '/api/v1/clusters/' + cluster_name, query)
		res = self.load_output(output)
		return res
	
	def set_username(self, user):
		self.username = user
		client.set_username(self.username)
		
	def set_password(self, password):
		self.password = password
		client.set_password(self.password)
		
	def set_proto(self, proto):
		self.proto = proto
		client.set_proto(self.proto)
	
	def set_server(self, server):
		self.server = server
		client.set_server(self.server)
	
	def set_username(self, user):
		self.username = user
		client.set_username(self.username)
		
	
	def __init__(self, username='', password='', proto='http', server='127.0.0.1', port=''):
		self.client = CurlClient()
		if not username == '':
			self.client.set_username(username)
			
		if not password == '':
			self.client.set_password(password)
			
		if not proto == '':
			self.client.set_proto(proto)
		
		if not server == '':
			self.client.set_server(server)
			
		if not str(port) == '':
			self.client.set_port(port)