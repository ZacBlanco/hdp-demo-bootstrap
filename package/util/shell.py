import os, subprocess
from logs import Logger

logger = Logger('Shell').getLogger()

# The shell class defines just a few functions which can make executing commands easier
# run
# 	This command has two possible ways to be called
# 	(command) which is just a single line with all arguments
# 	(command, args) which simply just joins a string with the command and arguments
# 
# It is also possible to change the current working directory (cwd)
# for commands which are sensitive to file locations
# (Unfortunately 'cd' doesn't work)

# If no arguments are passed for args, then it is assumed to be a string of length 0
# If no arguments are passed to the constructor we assume default cwd

class Shell:
	
	cwd = ''

	def run(self, command, args=''):
		
		if len(args) > 0:
			command = ' '.join([command, args.join(' ')])
		
		path = os.getcwd()
		if len(self.cwd) > 0:
			logger.debug('Working Directory: ' + self.cwd)
			logger.info('Running Command: ' + command)
			process = subprocess.Popen(command, shell=True, cwd=path, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
		else:
			process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
		output = process.communicate()
		return output


	# set_cwd
	# equivalent to doing a 'cd' command at the command line
	# Error if the directory doesn't exist
	def set_cwd(self, new_cwd):
		if not os.path.exists(new_cwd):
			logger.error('Directory ' + new_cwd + ' does not exist')
			raise IOError(' '.join([self.cwd, 'does not exist']))
		else:
			self.cwd = new_cwd

	def __init__(self, wd=''):
		if not wd == '':
			self.set_cwd(wd)
		