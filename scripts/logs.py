import logging, config, sys

class Logger():
	
	logger = logging.getLogger('init')
	
	def getLoggingLevel(self):
		try:
			conf = config.read_config('global-config.conf')['LOGGING']
			level = conf['log-level']
			if 'DEBUG' == level:
				return logging.DEBUG
			elif 'INFO' == level:
				return logging.INFO
			elif 'WARN' == level:
				return logging.WARN
			elif 'ERROR' == level:
				return logging.ERROR
			elif 'CRITICAL' == level:
				return logging.CRITICAL
			else:
				return logging.WARN
		except:
			return logging.WARN
	
	def getLogger(self):
		return self.logger
	
	def __init__(self, name):
		self.logger = logging.getLogger(name)
		sh = logging.StreamHandler(sys.stdout)
		sh.setLevel(self.getLoggingLevel())
		sh.setFormatter(logging.Formatter('[%(levelname)s] | %(name)s | %(message)s'))
		self.logger.addHandler(sh)
