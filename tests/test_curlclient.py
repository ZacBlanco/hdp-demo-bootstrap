import unittest, mock, env
from mock import MagicMock, Mock
from package.util.curl_client import CurlClient

res1 = ['\'key1\':value1', '']
res2 = ['\'key2\':value2', '']
res3 = ['\'key3\':value3', '']
resErr = ['', '\'msg\':\'err\'']

def mocked_request(*args, **kwargs):
	if '/api/v1/test' in args[0]:
		return res1
	elif '/api/v1/bad' in args[0]:
		return res2
	else:
		return res3
	return resErr
	
class TestCurlClient(unittest.TestCase):
	
	@mock.patch('package.util.shell.Shell.run', side_effect=mocked_request)
	def test_basic_command(self, mock_get):
		un = 'admin'
		pw = 'admin'
		pt = 9090
		serv = 'demo-server'
		prtc = 'http'
		client = CurlClient(username=un, password=pw, port=pt, server=serv, proto=prtc)
		assert client.username == un
		assert client.password == pw
		assert client.port == pt
		assert client.server == serv
		assert client.proto == prtc
		output = client.make_request('GET', '/api/v1/test')
		assert output == res1
		output = client.make_request('GET', '/api/v1/bad')
		assert output == res2
		output = client.make_request('GET', '')
		assert output == res3
		
	def test_bad_port(self):
		ports = [-1, 0, 65536, 'strPort']
		for pt in ports:
			try:
				client = CurlClient(port=pt)
				self.fail('Cannot set port to ' + str(port))
			except ValueError:
				pass
		
	def test_bad_proto(self):
		protos = ['http', 'https']
		
		for prtc in protos:
			try:
				client = CurlClient(proto=prtc)
			except ValueError:
				self.fail('Cannot set protocol to ' +proto)
		
		bad_protos = ['htp', 'thrift', 'odbc']
		for prtc in bad_protos:
			try:
				client = CurlClient(proto=prtc)
				self.fail('Cannot set protocol to ' +proto)
			except ValueError:
				pass
	
#	@mock.patch('package.util.shell.Shell.run', side_effect=mocked_request)
	def test_http_verbs(self):
		client = CurlClient()
		
		verbs = ['GET', 'PUT', 'POST', 'DELETE']
		bad_verbs = ['BAD', 'IAMBAD', 'IAMSUPERBAD']
		
		for v in verbs:
			try:
				client.make_request(v, '/')
			except:
				self.fail('Should not throw error on verb: ' + v)
		
		for v in bad_verbs:
			try:
				client.make_request(v, '/')
				self.fail('Should throw error on verb: ' + v)
			except:
				pass
			
			
			
			
			
			
			
			
			
			
			
			
		