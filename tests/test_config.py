import mock, unittest
from env import scripts
from scripts import config
from ConfigParser import MissingSectionHeaderError

class TestConfig(unittest.TestCase):

	@mock.patch('scripts.config.get_conf_dir', return_value='')
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

	@mock.patch('scripts.config.get_conf_dir', return_value='')
	def test_missing_header(self, mock1):
		try:
			params = config.read_config('res/bad-test.properties')
			assert 0
		except MissingSectionHeaderError as err:
			assert 1

	@mock.patch('scripts.config.get_conf_dir', return_value='')
	def test_missing_file(self, mock1):
		try:
			params = config.read_config('nofile')
			assert 0
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
			assert 'conf/' in cdir
		except EnvironmentError as e:
			assert str(e) == 'Could not find conf directory'
