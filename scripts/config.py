import os, ConfigParser


# readConfig
# Arguments : a relative path to the file
#
#	This function uses the working directory.
#	os.getcwd() is the working directory of the file/function
#	which called readConfig
#	The path to configFile is appended to the cwd
#
# All params are read as strings

def read_config(configFile):
	path = get_conf_dir() + configFile
	
	if not os.path.isfile(path):
		raise IOError('could not find file at '+path )
	
	config = ConfigParser.ConfigParser()
	config.read(path)
	params = {}
	
	for section in config.sections():
		params[section] = {}
		for key in config.options(section):
			params[section][key] = config.get(section, key)
	
	return params

def get_conf_dir():
	dirs = [str(os.getcwd()), str(os.curdir), '../']
	
	for loc in dirs:
		if not (str(loc).endswith('/')):
			loc += '/'
		loc += 'conf/'
		if(os.path.exists(loc)):
			return loc
	
	raise EnvironmentError('Could not find conf directory')
	
	
	