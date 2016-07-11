import mock, unittest, env, os, glob
from package.util import config
from ConfigParser import MissingSectionHeaderError

class TestConfig(unittest.TestCase):

	@mock.patch('package.util.config.get_conf_dir', return_value='')
	def test_good_file(self, mock1):
		params = config.read_config('res/good-test.properties')
		assert params['SECTION1']['key1'] == 'val1'
		assert params['SECTION2']['key2'] == 'val2'
		assert params['SECTION3']['key3'] == 'val3'
		assert params['SECTION3']['key4'] == 'val4'
		assert len(params['SECTION3']) > 1
		assert len(params['SECTION2']) > 0
		assert len(params['SECTION1']) > 0
		assert len(params) == 3

	@mock.patch('package.util.config.get_conf_dir', return_value='')
	def test_missing_header(self, mock1):
		try:
			params = config.read_config('res/bad-test.properties')
			assert 0
		except MissingSectionHeaderError as err:
			assert 1

	@mock.patch('package.util.config.get_conf_dir', return_value='')
	def test_missing_file(self, mock1):
		try:
			params = config.read_config('nofile')
			params = config.read_xml_config('nofile')
			self.fail('Should have thrown IOError')
		except IOError as e:
			if 'could not find file' not in e.message:
				assert 0
				
		try:
			params = config.read_xml_config('nofile')
			self.fail('Should have thrown IOError')
		except IOError as e:
			if 'could not find file' not in e.message:
				assert 0

	@mock.patch('os.path.exists', return_value=False)
	def test_bad_env(self, mock1):
		try:
			config.get_conf_dir()
			assert 0
		except EnvironmentError as e:
			assert str(e) == 'Could not find conf directory'

			
	@mock.patch('os.path.exists', return_value=True)
	@mock.patch('os.getcwd', return_value='adir')
	def test_good_env(self, mock1, mock2):
		try:
			cdir = config.get_conf_dir()
			assert 'configuration/' in cdir
		except EnvironmentError as e:
			assert str(e) == 'Could not find conf directory'
			
	@mock.patch('package.util.config.get_conf_dir', return_value='')
	def test_xml_tree(self, mock1):
		try:
			conf = config.read_xml_config('res/config/test-conf-1.xml')
			print(conf.keys())
			for i in range(1, 5):
				assert (conf['name.prop.' + str(i)] == 'val' + str(i))
		except IOError as e:
			self.fail(e)
			
	
	@mock.patch('package.util.config.get_conf_dir', return_value='./res/config/')
	@mock.patch('glob.glob', return_value=['./res/config/test-conf-1.xml', 'nofile', 'nofile2'])
	def test_missing_xml_files(self, mock1, mock2):
		try:
			conf = config.get_config()
			
			assert len(conf['configurations'].keys()) == 1
			for i in range(1, 5):
				assert (conf['configurations']['test-conf-1']['name.prop.' + str(i)] == 'val' + str(i))
		except IOError as e:
			self.fail(e)
			
		
	@mock.patch('package.util.config.get_conf_dir', return_value='')
	def test_bad_xml_tree(self, mock1):
		try:
			conf = config.read_xml_config('res/config/test-conf-3.xml')
			for i in range(3, 5):
				assert (conf['name.prop.' + str(i)] == 'val' + str(i))
			try:
				v = conf['name.prop.1']
				self.fail('Should have thrown KeyError')
			except KeyError as e:
				pass
			try:
				v = conf['name.prop.2']
				self.fail('Should have thrown KeyError')
			except KeyError as e:
				pass
			
		except IOError as e:
			self.fail(e)
					
			
	@mock.patch('package.util.config.get_conf_dir', return_value=os.path.dirname(os.path.abspath(__file__)) + "/res/config/")
	def test_xml_tree(self, mock1):
		try:
			conf = config.get_config()
			files = ['test-conf-1', 'test-conf-2']
			for f in files:
				for i in range(1, 5):
					assert (conf['configurations'][f]['name.prop.' + str(i)] == 'val' + str(i))
		except IOError as e:
			self.fail(e)
			
			
			
			
			
			
			
			
			
			
			
			
			
			
