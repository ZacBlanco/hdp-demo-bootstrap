import unittest, json, mock
from env import scripts
from mock import Mock
from scripts.ambari import Ambari


sample_cluster_res = '{"href":"http://demo-server:8080/api/v1/clusters","items":[{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster","Clusters":{"cluster_name":"demo_cluster","version":"HDP-2.4"}}]}'

sample_services_res = '{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster?fields=services","Clusters":{"cluster_name":"demo_cluster","version":"HDP-2.4"},"services":[{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/ACCUMULO","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"ACCUMULO"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/AMBARI_METRICS","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"AMBARI_METRICS"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/ATLAS","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"ATLAS"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/FALCON","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"FALCON"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/HBASE","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"HBASE"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/HDFS","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"HDFS"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/HIVE","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"HIVE"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/KAFKA","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"KAFKA"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/MAPREDUCE2","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"MAPREDUCE2"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/OOZIE","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"OOZIE"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/PIG","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"PIG"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/SPARK","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"SPARK"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/STORM","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"STORM"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/TEZ","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"TEZ"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/YARN","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"YARN"}},{"href":"http://demo-server:8080/api/v1/clusters/demo_cluster/services/ZOOKEEPER","ServiceInfo":{"cluster_name":"demo_cluster","service_name":"ZOOKEEPER"}}]}'

no_cluster_res = '{"status":404,"message":"The requested resource doesn\'t exist: Cluster not found, clusterName=d"}'

err_res = 'error message here'
empty_res = ''
bad_res = '{}]}}}'
bad_err_res = '{}{}{}{}{}{}{}{}STRY()'

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
	
	
	@mock.patch('scripts.shell.Shell.run', side_effect=mocked_request)
	def test_clusters_request(self, mock):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		data = client.getClusters();
		assert 'demo-server:8080' in data['href']
		assert data['items'][0]['Clusters']['cluster_name'] == 'demo_cluster'
		assert data['items'][0]['Clusters']['version'] == 'HDP-2.4'
		

	@mock.patch('scripts.shell.Shell.run', side_effect=mocked_request)	
	def test_services_request(self, mock):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		data = client.getServices('demo_cluster');
		assert 'demo-server:8080' in data['href']
		assert len(data['services']) == 16
		
	
	@mock.patch('scripts.shell.Shell.run', side_effect=mocked_request)
	def test_cluster_info_request(self, mock):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		data = client.getClusterInfo('demo_cluster');
		assert 'demo-server:8080' in data['href']
		assert len(data['services']) == 16
		
	@mock.patch('scripts.shell.Shell.run', side_effect=mocked_request)
	def test_missing_cluster(self, mock):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		data = client.getClusterInfo('');
		assert data['status'] == 404
		assert 'resource doesn\'t exist' in data['message']
		
	@mock.patch('scripts.shell.Shell.run', side_effect=mocked_request)
	def test_err_str(self, mock):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		data = client.getClusterInfo('bad/request');
		assert not len(data['message']) == 0
		assert data['message'] == err_res
		
	@mock.patch('scripts.shell.Shell.run', side_effect=mocked_request)
	def test_empty_str(self, mock):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		data = client.getClusterInfo('empty/res');
		assert not len(data['message']) == 0
		assert data['message'] == 'No output was returned.'
		
	@mock.patch('scripts.shell.Shell.run', side_effect=mocked_request)
	def test_bad_json_res(self, mock):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		try:
			data = client.getClusterInfo('bad/json/res');
			self.fail('Should have thrown an exception: ValueError')
		except ValueError as e:
			assert ('Extra data:' in str(e.message))
			assert not len(str(e.message)) == 0
			pass
		
	@mock.patch('scripts.shell.Shell.run', side_effect=mocked_request)
	def test_err_json_res(self, mock):
		client = Ambari(self.un, self.pw, self.proto, self.server, self.port)
		data = client.getClusterInfo('err/json/res');
		assert not len(str(data['message'])) == 0
		assert data['message'] == bad_err_res
		
		
		
		
		
		
		
		
		