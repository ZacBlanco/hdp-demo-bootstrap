# Script which installs Zeppelin as an Ambari Service
import config, sys, platform, json, time
from shell import Shell
from curl_client import CurlClient

def install_hdp_select():
	dist_info = platform.linux_distribution()
	if(len(dist_info[0]) == 0):
		raise EnvironmentError('You must be running a linux distribution to install hdp-select')
		
#	Only want to get distro name
#	Determine first distro name
#		Then determine the version (first char char for centos )
	distro = dist_info[0].lower()
	fullname = distro
	ver = dist_info[1]
	if 'centos' in distro: # Get First 1/2 nums in version string
		fullname = fullname + dist_info[1][0]
	elif 'ubuntu' in distro:
		if (len(dist_info[1]) < 2):
			fullname = fullname + dist_info[1][0]
		else:
			fullname = fullname + dist_info[1][0] + dist_info[1][1]
	
	conf = config.read_config('../conf/service-installer.conf')
	urls = conf['HDP-SELECT']
	url = ''
	if fullname == 'centos6':	
		url = urls['centos6']
	elif fullname == 'centos7':
		url = urls['centos7']
	elif fullname == 'ubuntu12':
		url = urls['ubuntu12']
	elif fullname == 'ubuntu14':
		url = urls['ubuntu14']
	
	res = ''
	
	if len(url) == 0:
		raise EnvironmentError('Must be using one of: CentOS 6.x, CentOS 7.x, Ubuntu 12.x, Ubuntu 14.x')
	elif 'centos' in fullname:
		cmd = Shell()
		output = cmd.run('yum install -y ' + url)
		res = cmd.run('which hdp-select')
	elif 'ubuntu' in fullname:
		cmd = Shell()
		output = cmd.run('wget ' + url + ' -O ./hdp-select.deb')
		output = cmd.run('dpkg -i ' + './hdp-select.deb')
		res = cmd.run('which hdp-select')
		
	if len(res[0]) == 0:
		return False
	else:
		return True

def is_hdp_select_installed():
	sh = Shell()
	output = sh.run('which hdp-select')
	
	if len(output[0]) == 0:
		return False
	else:
		return True

def is_ambari_installed():
	sh = Shell()
	output = sh.run('which ambari-server')
	if len(output[0]) == 0:
		return False
	else:
		return True


def install_zeppelin(conf_dir):
	
	if not conf_dir.endswith('/'):
		conf_dir += '/'
	
	if not is_ambari_installed():
		raise EnvironmentError('You must install the demo on the same node as the Ambari server. Install Ambari here or move to another node with Ambari installed before continuing')
	
	
	if not is_hdp_select_installed():
		installed = install_hdp_select()
		if not installed:
			raise EnvironmentError('hdp-select could not be installed. Please install it manually and then re-run the setup.')
	
	conf = config.read_config(conf_dir + 'service-installer.conf')
	cmds = conf['ZEPPELIN']['install-commands']
	cmds = json.loads(conf['ZEPPELIN']['install-commands'])
	
	sh = Shell()
#	print(sh.run('pwd')[0])
	version = sh.run(cmds[0])
#	print("HDP-VERSION: " + str(version[0]))
	fixed_cmd = cmds[1].replace('$VERSION', str(version[0])).replace('\n', '')
#	print('FIXED COPY COMMAND: ' + fixed_cmd)
	copy = sh.run(fixed_cmd)
#	print("COPY OUTPUT: " + copy[0])
	restart = sh.run(cmds[2])
#	print("Restart output: " + restart[0])


	print("Please open the Ambari Interface and manually deploy the Zeppelin Service.")
	raw_input("Press enter twice to continue...")
	raw_input("Press enter once to continue...")
	
#	 We've copied the necessary files. Once that completes we need to add it to Ambari
	
	print('Checking to make sure service is installed')
	ambari = config.read_config(conf_dir + 'global-config.conf')['AMBARI']
	installed = check_ambari_service_installed('ZEPPELIN', ambari)
	cont = ''
	if not installed:
		print('Unable to contact Ambari Server. Unsure whether or not Zeppelin was installed')
		while not (cont == 'y' or cont == 'n'):
			cont = raw_input('Continue attempt to set up Zeppelin for demo?(y/n)')
			if not (cont == 'y' or cont == 'n'):
				print('Please enter "y" or "n"')
	else:
		cont = 'y'
	
	if cont == 'n':
		return False
	elif cont == 'y':
		return True



def install_nifi(conf_dir):
	
	if not conf_dir.endswith('/'):
		conf_dir += '/'
	
	if not is_ambari_installed():
		raise EnvironmentError('You must install the demo on the same node as the Ambari server. Install Ambari here or move to another node with Ambari installed before continuing')
	
	
	if not is_hdp_select_installed():
		installed = install_hdp_select()
		if not installed:
			raise EnvironmentError('hdp-select could not be installed. Please install it manually and then re-run the setup.')

	conf = config.read_config(conf_dir + 'service-installer.conf')
	cmds = json.loads(conf['NIFI']['install-commands'])
	
	sh = Shell()
#	print(sh.run('pwd')[0])
	version = sh.run(cmds[0])
#	print("HDP-VERSION: " + str(version[0]))
	fixed_copy = cmds[2].replace('$VERSION', str(version[0])).replace('\n', '')
#	print('FIXED COPY COMMAND: ' + fixed_cmd)
	fixed_remove = cmds[1].replace('$VERSION', str(version[0])).replace('\n', '')
	remove = sh.run(fixed_remove)
	copy = sh.run(fixed_copy)
#	print("COPY OUTPUT: " + copy[0])
	restart = sh.run(cmds[3])
#	print("Restart output: " + restart[0])


	print("Please open the Ambari Interface and manually deploy the NiFi Service.")
	raw_input("Press enter twice to continue...")
	raw_input("Press enter once to continue...")
	
#	 We've copied the necessary files. Once that completes we need to add it to Ambari
	
	print('Checking to make sure service is installed')
	ambari = config.read_config(conf_dir + 'global-config.conf')['AMBARI']
	installed = check_ambari_service_installed('NIFI', ambari)
	cont = ''
	if not installed:
		print('Unable to contact Ambari Server. Unsure whether or not Zeppelin was installed')
		while not (cont == 'y' or cont == 'n'):
			cont = raw_input('Continue attempt to set up NiFi for demo?(y/n)')
			if not (cont == 'y' or cont == 'n'):
				print('Please enter "y" or "n"')
	else:
		cont = 'y'
	
	if cont == 'n':
		return False
	elif cont == 'y':
		return True


	
def check_ambari_service_installed(service_name, ambari_config):
	
	curl = CurlClient(username=ambari_config['username'], password=ambari_config['password'], port=ambari_config['port'], server=ambari_config['server'], proto=ambari_config['proto'])
	
	cluster_name = ambari_config['cluster_name']
	request = '/api/v1/clusters/' + cluster_name + '/services/' + service_name
	attempts = 0
	while attempts < 10:
		output = curl.make_request('GET', request, '-i')
		if '200 OK' in output[0]:
			print('Service Installed Sucessfully')
			return True
		else:
			attempts += 1
			raw_input('Could not connect.' + str(10-attempts) + ' remaining. Press any key to continue')
	
	return False












	
	
	