import sys, pwd, grp
from resource_management import *
from resource_management.core.exceptions import ComponentIsNotRunning
from subprocess import call
reload(sys)
sys.setdefaultencoding('utf8')

# INSTRUCTIONS ON IMPLEMENTING SERVICE METHODS
# 
# Note: all of this information can be found
# under ./docs/ambari-service.md
# 
# Install
#  - Installs any necessary components for the service
# Start
#  - Starts any necessary services
# Stop
#  - Stops any service components
# Status
#  - Gets the status of the components
# Configure
#  - Writes out configuration details from Ambari to the services configuration files


class Master(Script):
    
  def create_linux_user(self, user, group):
    try:
      pwd.getpwnam(user)
    except KeyError:
      Execute('adduser ' + user)
    try:
      grp.getgrnam(group)
    except KeyError:
      Execute('groupadd ' + group)

  def install(self, env):
    import params
    print 'Install the Demo Service Master';
    self.create_linux_user(params.demo_user, params.demo_group)
    if params.demo_user != 'root':
      Execute('cp /etc/sudoers /etc/sudoers.bak')        
      Execute('echo "' + params.demo_user + '    ALL=(ALL)       NOPASSWD: ALL" >> /etc/sudoers')
      
    Execute('mkdir -p '+ params.demo_pid_dir + ' ' + params.demo_log_dir)
    Execute('chown -R ' + params.demo_user + ':' + params.demo_group + ' ' + params.demo_pid_dir)
    Execute('chown -R ' + params.demo_user + ':' + params.demo_group + ' ' + params.demo_log_dir)
    
    # Ensure pip is instaled
    Execute('sudo yum install python-pip')
    Execute('pip install -r ' + '/'.join([params.demo_bin_dir, 'requirements.txt']))

  def stop(self, env):
		# Fill me in!
    import params
    print 'Stop the Demo Service Master'
    Execute('kill `cat ' + params.demo_pid_file + '`' )

  def start(self, env):
    print 'Start the Demo Service Master'
    import params
		# Fill me in!
    Execute('nohup python ' + params.demo_bin_dir +  '/demo-server.py &')
    Execute('cp ' + params.demo_bin_dir + '/demo.pid ' + params.demo_pid_file)
    
  def status(self, env):
    print 'Status of the Demo Service Master'
    import params
		# Fill me in!
    check_process_status(params.demo_pid_file)
    
  def configure(self, env):
    pass
		# Fill me in!
		# print 'Configure the Demo Service Master';


if __name__ == "__main__":
	Master().execute()
	