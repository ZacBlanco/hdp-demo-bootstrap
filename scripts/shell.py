import os, subprocess

class Shell:
	
	cwd = ''

	def run(self, command, args=''):
		
		if len(args) > 0:
			command = ' '.join([command, args.join(' ')])
		
		path = os.getcwd()
		if len(self.cwd) > 0:
			process = subprocess.Popen(command, shell=True, cwd=path, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
		else:
			process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
		output = process.communicate()
		return output


	# set_cwd
	# equivalent to doing a 'cd' command at the command line
	def set_cwd(self, new_cwd):
		if not os.path.exists(new_cwd):
			raise IOError(' '.join([self.cwd, 'does not exist']))
		else:
			self.cwd = new_cwd

	def __init__(self, wd=''):
		if not wd == '':
			self.set_cwd(wd)
		