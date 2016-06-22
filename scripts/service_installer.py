# Script which installs Zeppelin as an Ambari Service
import config, sys, platform, json
from shell import Shell

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
		
	if len(res) == 0:
		return False
	else:
		return True

def is_hdp_select_installed():
	sh = Shell()
	output = sh.run('which hdp-select')
	if len(output) == 0:
		return False
	else:
		return True
















	
	
	