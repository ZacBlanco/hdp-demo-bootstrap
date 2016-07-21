import os, ConfigParser, glob
import xml.etree.ElementTree as ET


# readConfig
# Arguments : a relative path to the file
#
#	This function uses the working directory.
#	os.getcwd() is the working directory of the file/function
#	which called readConfig
#	The path to configFile is appended to the cwd
#
# All params are read as strings

def read_config(config_file):
	
	path = get_path(config_file)
	
	config = ConfigParser.ConfigParser()
	config.read(path)
	params = {}
	
	for section in config.sections():
		params[section] = {}
		for key in config.options(section):
			params[section][key] = config.get(section, key)
	
	return params

def read_xml_config(config_file):
	path = get_path(config_file)
	config_root = ET.parse(path).getroot()
	conf = {}
	# Get all property elements
	for prop in config_root.findall('property'):
		
		nm = prop.find('name')
		val = prop.find('value')
		if not (nm == None or val == None):
			conf[nm.text] = val.text
			
	return conf

# Raises an IOError if the file doesn't exist
# Returns the path to the file if it does
def get_path(config_file):
	path = get_conf_dir() + config_file
	
	exists = False
	
	if os.path.isfile(path):
		exists = True
	elif os.path.isfile(config_file):
		path = config_file
		exists = True
		
	if not exists:
		raise IOError('Could not find file at ' + config_file + ' or ' + path)
	
	return path
	
# returns a dict with dict['configurations'] containing
# another dict with a list of file names
# Under each filename is the parameters

def get_config():
	conf = {}
	conf['configurations'] = {}
	
	conf_dir = get_conf_dir()
	dir_entries = glob.glob(conf_dir + "*.xml" )
	print dir_entries
	for conf_file in dir_entries:
		if os.path.isfile(conf_file):
			path, filename = os.path.split(conf_file)
			name = os.path.splitext(filename)[0]
			print(filename)
			print conf_file
			params = read_xml_config(filename)
			conf['configurations'][name] = params
	
	return conf
	
	
	


# Gets full path to configuration directory. Always ends with a forward slash (/)
def get_conf_dir():
	dirs = [str(os.getcwd()), str(os.curdir), '../', os.path.dirname(os.path.abspath(__file__)) + '/../..']
	
	for loc in dirs:
		if not (str(loc).endswith('/')):
			loc += '/'
		loc += 'configuration/'
		if(os.path.exists(loc)):
#			print('LOCATION: ' + loc)
			return loc
	raise EnvironmentError('Could not find conf directory')
	
	
	