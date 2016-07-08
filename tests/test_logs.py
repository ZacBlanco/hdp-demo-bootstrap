import mock, unittest, env
from package.util.logs import Logger


class TestLogs(unittest.TestCase):

	@mock.patch('package.util.config.read_config', return_value={'LOGGING': {'log-level': 'DEBUG'}})
	def test_debug(self, mock1):
		logger = Logger('debug').getLogger()
		handler = logger.handlers[0]
		assert handler.level == 10
		
	@mock.patch('package.util.config.read_config', return_value={'LOGGING': {'log-level': 'INFO'}})
	def test_info(self, mock1):
		logger = Logger('info').getLogger()
		handler = logger.handlers[0]
		print("LOGLEVEL: " + str(logger.handlers))
		assert handler.level == 20
	
	@mock.patch('package.util.config.read_config', return_value={'LOGGING': {'log-level': 'WARN'}})
	def test_warn(self, mock1):
		logger = Logger('warning').getLogger()
		handler = logger.handlers[0]
		assert handler.level == 30
	
	@mock.patch('package.util.config.read_config', return_value={'LOGGING': {'log-level': 'ERROR'}})
	def test_error(self, mock1):
		logger = Logger('error').getLogger()
		handler = logger.handlers[0]
		assert handler.level == 40
	
	@mock.patch('package.util.config.read_config', return_value={'LOGGING': {'log-level': 'CRITICAL'}})
	def test_critical(self, mock1):
		logger = Logger('critical').getLogger()
		handler = logger.handlers[0]
		assert handler.level == 50
		
	@mock.patch('package.util.config.read_config', return_value={'LOGGING': {'log-level': 'CRITICAL'}})
	def test_handler(self, mock1):
		logger = Logger('name').getLogger()
		handler = logger.handlers[0]
		assert handler.level == 50
		print('HANDLER NAME: ' +logger.name)
		
	@mock.patch('package.util.config.read_config', return_value={'LOGGING': {'log-level': 'MISSING'}})
	def test_missing(self, mock1):
		logger = Logger('bad_level_test').getLogger()
		handler = logger.handlers[0]
		assert handler.level == 30

	@mock.patch('package.util.config.read_config', return_value={'LOGGING': {'bad-level': 'MISSING'}})
	def test_bad(self, mock1):
		logger = Logger('missing_level').getLogger()
		handler = logger.handlers[0]
		assert handler.level == 30