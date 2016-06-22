import unittest, json, mock
from env import scripts
from mock import Mock
from scripts import service_installer

non_linux_distro = ['', '', '']
other_linux_distro = ['mint', '', '']
centos_6_distro = ['CentOS', '6.8', 'Final']
centos_7_distro = ['CentOS', '6.8', 'Final']
ubuntu_12_distro = ['Ubuntu', '12.04', 'precise']
ubuntu_14_distro = ['Ubuntu', '14.04', 'trusty']
bad_ubuntu = ['Ubuntu', '1', 'NaN']

#def mocked_cmd(*args, **kwargs):
#	print("ARGS: " + ', '.join(args))
#	
#	if 'centos6' in args[0]:
#		return centos_6_distro
#	elif 'centos7' in args[0]:
#		return centos_7_distro
#	elif 'ubuntu12' in args[0]:
#		return ubuntu_12_distro
#	elif 'ubuntu14' in args[0]:
#		return ubuntu_14_distro
#	elif 'nonlinux' in args[0]:
#		return non_linux_distro
#	

class TestHDPSelectInstall(unittest.TestCase):
	
	@mock.patch('platform.linux_distribution', return_value=centos_6_distro)
	@mock.patch('scripts.shell.Shell.run', return_value='/usr/bin/hdp-select')
	def test_hdp_select_centos_6(self, mock, mock2):
		assert True == service_installer.install_hdp_select()
		
	
	@mock.patch('platform.linux_distribution', return_value=centos_7_distro)
	@mock.patch('scripts.shell.Shell.run', return_value='/usr/bin/hdp-select')
	def test_hdp_select_centos_7(self, mock, mock2):
		assert True == service_installer.install_hdp_select()
	
	@mock.patch('platform.linux_distribution', return_value=ubuntu_12_distro)
	@mock.patch('scripts.shell.Shell.run', return_value='/usr/bin/hdp-select')
	def test_hdp_select_ubuntu_12(self, mock, mock2):
		assert True == service_installer.install_hdp_select()
		
	@mock.patch('platform.linux_distribution', return_value=ubuntu_14_distro)
	@mock.patch('scripts.shell.Shell.run', return_value='/usr/bin/hdp-select')
	def test_hdp_select_ubuntu_14(self, mock, mock2):
		assert True == service_installer.install_hdp_select()
		
		
	@mock.patch('platform.linux_distribution', return_value=centos_6_distro)
	@mock.patch('scripts.shell.Shell.run', return_value='')
	def test_hdp_select_centos_6(self, mock, mock2):
		assert False == service_installer.install_hdp_select()
	
	@mock.patch('platform.linux_distribution', return_value=centos_7_distro)
	@mock.patch('scripts.shell.Shell.run', return_value='')
	def test_hdp_select_centos_7(self, mock, mock2):
		assert False == service_installer.install_hdp_select()
	
	@mock.patch('platform.linux_distribution', return_value=ubuntu_12_distro)
	@mock.patch('scripts.shell.Shell.run', return_value='')
	def test_hdp_select_ubuntu_12(self, mock, mock2):
		assert False == service_installer.install_hdp_select()
		
	@mock.patch('platform.linux_distribution', return_value=ubuntu_14_distro)
	@mock.patch('scripts.shell.Shell.run', return_value='')
	def test_hdp_select_ubuntu_14(self, mock, mock2):
		assert False == service_installer.install_hdp_select()
		
	@mock.patch('platform.linux_distribution', return_value=bad_ubuntu)
	@mock.patch('scripts.shell.Shell.run', return_value='')
	def test_hdp_select_ubuntu_14(self, mock, mock2):
		try:
			service_installer.install_hdp_select()
			self.fail('Should fail with a non-linux operating system')
		except EnvironmentError as e:
			assert str(e.message) == 'Must be using one of: CentOS 6.x, CentOS 7.x, Ubuntu 12.x, Ubuntu 14.x'
		
	
	@mock.patch('platform.linux_distribution', return_value=non_linux_distro)
	@mock.patch('scripts.shell.Shell.run', return_value='/usr/bin/hdp-select')
	def test_hdp_select_non_linux(self, mock, mock2):
		try:
			service_installer.install_hdp_select()
			self.fail('Should fail with a non-linux operating system')
		except EnvironmentError as e:
			assert str(e.message) == 'You must be running a linux distribution to install hdp-select'
			
	@mock.patch('platform.linux_distribution', return_value=other_linux_distro)
	@mock.patch('scripts.shell.Shell.run', return_value='/usr/bin/hdp-select')
	def test_hdp_select_other_linux(self, mock, mock2):
		try:
			service_installer.install_hdp_select()
			self.fail('Should fail with a non-linux operating system')
		except EnvironmentError as e:
			assert str(e.message) == 'Must be using one of: CentOS 6.x, CentOS 7.x, Ubuntu 12.x, Ubuntu 14.x'

class TestHDPSelectCheck(unittest.TestCase):

	@mock.patch('scripts.shell.Shell.run', return_value='/usr/bin/hdp-select')
	def test_hdp_select_good(self, mock):
		assert service_installer.is_hdp_select_installed() == True
			
	@mock.patch('scripts.shell.Shell.run', return_value='')
	def test_hdp_select_bad(self, mock):
			assert service_installer.is_hdp_select_installed() == False
	
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			