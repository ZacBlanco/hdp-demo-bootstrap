import unittest, json, mock, env
from mock import Mock
from package.util.ambari import Ambari


sample_cluster_res = '{"href":"http://demo-server:8080/api/v1/clusters","items":[{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster","Clusters":{"cluster_name":"demo_cluster","version":"HDP-2.4"}}]}'

sample_services_res = '{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster?fields=services","Clusters":{"cluster_name":"demo_cluster","version":"HDP-2.4"},"services":[{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/ACCUMULO","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"ACCUMULO"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/AMBARI_METRICS","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"AMBARI_METRICS"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/ATLAS","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"ATLAS"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/FALCON","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"FALCON"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/HBASE","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"HBASE"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/HDFS","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"HDFS"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/HIVE","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"HIVE"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/KAFKA","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"KAFKA"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/MAPREDUCE2","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"MAPREDUCE2"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/OOZIE","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"OOZIE"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/PIG","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"PIG"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/SPARK","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"SPARK"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/STORM","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"STORM"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/TEZ","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"TEZ"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/YARN","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"YARN"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/ZOOKEEPER","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"ZOOKEEPER"}}]}'

no_cluster_res = '{"status":404,"message":"The requested resource doesn\'t exist: Cluster not found, clusterName=d"}'

err_res = 'error message here'
empty_res = ''
bad_res = '{}]}}}'
bad_err_res = '{}{}{}{}{}{}{}{}STRY()'

service_info_stopped = """{
  "href" : "http://sandbox.hortonworks.com:8080/api/v1/clusters/Sandbox/services/YARN?fields=ServiceInfo",
  "ServiceInfo" : {
    "cluster_name" : "Sandbox",
    "maintenance_state" : "OFF",
    "service_name" : "YARN",
    "state" : "INSTALLED"
  }
}"""

service_info_started = """{
  "href" : "http://sandbox.hortonworks.com:8080/api/v1/clusters/Sandbox/services/YARN?fields=ServiceInfo",
  "ServiceInfo" : {
    "cluster_name" : "Sandbox",
    "maintenance_state" : "OFF",
    "service_name" : "YARN",
    "state" : "STARTED"
  }
}"""

service_info_starting = """{
  "href" : "http://sandbox.hortonworks.com:8080/api/v1/clusters/Sandbox/services/YARN?fields=ServiceInfo",
  "ServiceInfo" : {
    "cluster_name" : "Sandbox",
    "maintenance_state" : "OFF",
    "service_name" : "YARN",
    "state" : "STARTING"
  }
}"""

ambari_cluster_missing = """{
  "status" : 404,
  "message" : "Parent Cluster resource doesn't exist.  Cluster not found, clusterName=andbox.  Cluster not found, clusterName=andbox"
}"""

yarn_service_res = """{"href":"http://sandbox.hortonworks.com:8080/api/v1/clusters/Sandbox/services/YARN","ServiceInfo":{"cluster_name":"Sandbox","maintenance_state":"OFF","service_name":"YARN","state":"INSTALLED"},"alerts_summary":{"CRITICAL":0,"MAINTENANCE":0,"OK":0,"UNKNOWN":0,"WARNING":0},"alerts":[],"components":[{"href":"http://sandbox.hortonworks.com:8080/api/v1/clusters/Sandbox/services/YARN/components/APP_TIMELINE_SERVER","ServiceComponentInfo":{"cluster_name":"Sandbox","component_name":"APP_TIMELINE_SERVER","service_name":"YARN"}},{"href":"http://sandbox.hortonworks.com:8080/api/v1/clusters/Sandbox/services/YARN/components/NODEMANAGER","ServiceComponentInfo":{"cluster_name":"Sandbox","component_name":"NODEMANAGER","service_name":"YARN"}},{"href":"http://sandbox.hortonworks.com:8080/api/v1/clusters/Sandbox/services/YARN/components/RESOURCEMANAGER","ServiceComponentInfo":{"cluster_name":"Sandbox","component_name":"RESOURCEMANAGER","service_name":"YARN"}},{"href":"http://sandbox.hortonworks.com:8080/api/v1/clusters/Sandbox/services/YARN/components/YARN_CLIENT","ServiceComponentInfo":{"cluster_name":"Sandbox","component_name":"YARN_CLIENT","service_name":"YARN"}}],"artifacts":[]}"""

missing_service_res = """{
  "status" : 404,
  "message" : "The requested resource doesn't exist: Service not found, clusterName=Sandbox, serviceName=ay"
}"""

change_response_same = """HTTP/1.1 200 OK
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
User: admin
Set-Cookie: AMBARISESSIONID=145inun8385h1xdu1sr1tyuhb;Path=/;HttpOnly
Expires: Thu, 01 Jan 1970 00:00:00 GMT
Content-Type: text/plain
Content-Length: 0
Server: Jetty(8.1.17.v20150415)"""

change_response_diff = """HTTP/1.1 202 Accepted
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
User: admin
Set-Cookie: AMBARISESSIONID=1de6uutc3llox2dnodqn63yc9;Path=/;HttpOnly
Expires: Thu, 01 Jan 1970 00:00:00 GMT
Content-Type: text/plain
Vary: Accept-Encoding, User-Agent
Content-Length: 151
Server: Jetty(8.1.17.v20150415)

{
  "href" : "http://sandbox.hortonworks.com:8080/api/v1/clusters/Sandbox/requests/56",
  "Requests" : {
    "id" : 56,
    "status" : "Accepted"
  }
}"""
	
bad_res_diff = """HTTP/1.1 400 Bad Request
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
User: admin
Set-Cookie: AMBARISESSIONID=q9l3n2dt79mpoyn3mhfnzwf;Path=/;HttpOnly
Expires: Thu, 01 Jan 1970 00:00:00 GMT
Content-Type: text/plain
Content-Length: 107
Server: Jetty(8.1.17.v20150415)

{
  "status" : 400,
  "message" : "CSRF protection is turned on. X-Requested-By HTTP header is required."
}"""

def mocked_request(*args, **kwargs):
	
	if '/api/v1/clusters?' in args[0]:
		return [sample_cluster_res, '']
	elif ('/api/v1/clusters/demo_cluster?' in args[0]):
		return [sample_services_res, '']
	elif ('/api/v1/clusters/demo_cluster/services?' in args[0]):
		return [sample_services_res, '']
	elif ('bad/request' in args[0]):
		return ['', err_res]
	elif ('empty/res' in args[0]):
		return ['', empty_res]
	elif ('bad/json/res' in args[0]):
		return [bad_res, '']
	elif ('err/json/res' in args[0]):
		return ['', bad_err_res]
	else:
		return [no_cluster_res, '']

class TestAmbariClient(unittest.TestCase):
	
	un = 'admin'
	pw = 'admin'
	proto = 'http'
	server = 'demo-server'
	port = 8080
	
	
	@mock.patch('package.util.shell.Shell.run', side_effect=mocked_request)
	def test_clusters_request(self, mock):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		data = client.get_clusters();
		assert 'demo-server:8080' in data['href']
		assert data['items'][0]['Clusters']['cluster_name'] == 'demo_cluster'
		assert data['items'][0]['Clusters']['version'] == 'HDP-2.4'
		

	@mock.patch('package.util.shell.Shell.run', side_effect=mocked_request)	
	def test_services_request(self, mock):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		data = client.get_services('demo_cluster');
		assert 'demo-server:8080' in data['href']
		assert len(data['services']) == 16
		
	
	@mock.patch('package.util.shell.Shell.run', side_effect=mocked_request)
	def test_cluster_info_request(self, mock):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		data = client.get_cluster_info('demo_cluster');
		assert 'demo-server:8080' in data['href']
		assert len(data['services']) == 16
		
	@mock.patch('package.util.shell.Shell.run', side_effect=mocked_request)
	def test_missing_cluster(self, mock):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		data = client.get_cluster_info('');
		assert data['status'] == 404
		assert 'resource doesn\'t exist' in data['message']
		
	@mock.patch('package.util.shell.Shell.run', side_effect=mocked_request)
	def test_err_str(self, mock):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		data = client.get_cluster_info('bad/request');
		assert not len(data['message']) == 0
		assert data['message'] == err_res
		
	@mock.patch('package.util.shell.Shell.run', side_effect=mocked_request)
	def test_empty_str(self, mock):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		data = client.get_cluster_info('empty/res');
		assert not len(data['message']) == 0
		assert data['message'] == 'No output was returned.'
		
	@mock.patch('package.util.shell.Shell.run', side_effect=mocked_request)
	def test_bad_json_res(self, mock):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		try:
			data = client.get_cluster_info('bad/json/res');
			self.fail('Should have thrown an exception: ValueError')
		except ValueError as e:
			assert ('Extra data:' in str(e.message))
			assert not len(str(e.message)) == 0
			pass
		
	@mock.patch('package.util.shell.Shell.run', side_effect=mocked_request)
	def test_err_json_res(self, mock):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		data = client.get_cluster_info('err/json/res');
		assert not len(str(data['message'])) == 0
		assert data['message'] == bad_err_res
		
		
	def test_set_wait_time(self):
		client = Ambari(service_wait_time=-5)
		assert client.service_wait_time == 60
		client.set_service_wait_time(-9)
		assert client.service_wait_time == 60
		client.set_service_wait_time(50)
		assert client.service_wait_time == 50
		client.set_service_wait_time(25)
		assert client.service_wait_time == 25
		
	@mock.patch('package.util.shell.Shell.run', side_effect=[[yarn_service_res, ''], [missing_service_res, '']])
	def test_get_service(self, mock1):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		assert json.loads(yarn_service_res) == client.get_service('Sandbox', 'YARN') 
		assert json.loads(missing_service_res) == client.get_service('Sandbox', 'Ay') 
	
	@mock.patch('package.util.shell.Shell.run', return_value=[json.loads(service_info_stopped), ''])
	@mock.patch('package.util.ambari.Ambari.get_service', return_value=[json.loads(service_info_stopped), ''])
	@mock.patch('package.util.curl_client.CurlClient.make_request', return_value=[change_response_diff, ''])
	@mock.patch('time.sleep', return_value=1)
	def test_service_request_bad_action(self, mock1, mock2, mock3, mock4):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		
		try:
			client.service_action('Sandbox', 'YARN', 'STOP')
			client.service_action('Sandbox', 'YARN', 'START')
			client.service_action('Sandbox', 'YARN', 'RESTART')
			client.service_action('Sandbox', 'YARN', 'BAD_ACTION')
			self.fail('Should have thrown value error on BAD_ACTION')
		except ValueError as e:
			assert str(e) == 'Service action must be one of: START, STOP, or RESTART'
		
	@mock.patch('package.util.shell.Shell.run', side_effect=[[service_info_starting, ''], [service_info_starting, ''], [service_info_started, '']])
	@mock.patch('package.util.ambari.Ambari.get_service', return_value=[json.loads(service_info_stopped), ''])
	@mock.patch('package.util.curl_client.CurlClient.make_request', return_value=[change_response_diff, ''])
	def test_service_request_stopped(self, mock1, mock2, mock3):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		val = client.service_action('Sandbox', 'YARN', 'STOP')
		assert val == True
	
	@mock.patch('package.util.shell.Shell.run', side_effect=[[service_info_starting, ''], [service_info_starting, ''], [service_info_started, '']])
	@mock.patch('package.util.ambari.Ambari.get_service', return_value=[json.loads(service_info_started), ''])
	@mock.patch('package.util.curl_client.CurlClient.make_request', return_value=[change_response_same, ''])
	def test_service_request_started(self, mock1, mock2, mock3):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		
		val = client.service_action('Sandbox', 'YARN', 'START')
		assert val == True
	
	@mock.patch('package.util.shell.Shell.run', side_effect=[[service_info_starting, ''], [service_info_starting, ''], [service_info_started, '']])
	@mock.patch('package.util.ambari.Ambari.get_service', return_value=[json.loads(service_info_started), ''])
	@mock.patch('package.util.curl_client.CurlClient.make_request', return_value=[change_response_same, ''])
	@mock.patch('time.sleep', return_value=1)
	def test_service_request_stop(self, mock1, mock2, mock3, mock4):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		
		try:
			client.service_action('Sandbox', 'YARN', 'BAD_ACTION')
			self.fail('Should have thrown value error on BAD_ACTION')
		except ValueError as e:
			assert str(e) == 'Service action must be one of: START, STOP, or RESTART'
		
		val = client.service_action('Sandbox', 'YARN', 'STOP')
		assert val == False
	
	@mock.patch('package.util.shell.Shell.run', side_effect=[[service_info_stopped, ''], [service_info_stopped, ''], [service_info_stopped, '']])
	@mock.patch('package.util.ambari.Ambari.get_service', return_value=[json.loads(service_info_stopped), ''])
	@mock.patch('package.util.curl_client.CurlClient.make_request', return_value=[change_response_same, ''])
	@mock.patch('time.sleep', return_value=1)
	def test_service_request_start(self, mock1, mock2, mock3, mock4):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		
		try:
			client.service_action('Sandbox', 'YARN', 'BAD_ACTION')
			self.fail('Should have thrown value error on BAD_ACTION')
		except ValueError as e:
			assert str(e) == 'Service action must be one of: START, STOP, or RESTART'
		
		val = client.service_action('Sandbox', 'YARN', 'START')
		assert val == False
	
	@mock.patch('package.util.shell.Shell.run', side_effect=[[service_info_stopped, ''], [service_info_stopped, ''], [service_info_stopped, '']])
	@mock.patch('package.util.ambari.Ambari.get_service', return_value=[json.loads(service_info_stopped), ''])
	@mock.patch('package.util.curl_client.CurlClient.make_request', return_value=[change_response_same, ''])
	@mock.patch('time.sleep', return_value=1)
	def test_service_request_restart(self, mock1, mock2, mock3, mock4):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		
		val = client.service_action('Sandbox', 'YARN', 'RESTART')
		assert val == False
	
	@mock.patch('package.util.shell.Shell.run', side_effect=[[service_info_stopped, ''], [service_info_stopped, ''], [service_info_stopped, '']])
	@mock.patch('package.util.ambari.Ambari.get_service', return_value=[json.loads(service_info_stopped), ''])
	@mock.patch('package.util.curl_client.CurlClient.make_request', return_value=[bad_res_diff, ''])
	@mock.patch('time.sleep', return_value=1)
	def test_service_request_bad_req(self, mock1, mock2, mock3, mock4):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		
		val = client.service_action('Sandbox', 'YARN', 'STOP')
		assert val == False
				
		
		
		
		
		
		
		
		
		
		
		
		