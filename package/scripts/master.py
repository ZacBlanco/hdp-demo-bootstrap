import sys, pwd, grp
import resource_management
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
#    params.demo_conf_install_dir
#    print(Execute('mkdir -p ' + params.demo_conf_install_dir))
#    Execute('git clone ' + params.demo_conf_pull_url + ' ' + params.demo_conf_install_dir)
    
    self.create_linux_user(params.demo_user, params.demo_group)
    self.configure(env)
    print 'Install the Demo Service Master';
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
    try:
      Execute('kill `cat ' + params.demo_pid_file + '`' )
    except resource_management.core.exceptions.Fail as e:
      pass

  def start(self, env):
    print 'Start the Demo Service Master'
    import params
    self.configure(env)
    Execute('nohup python ' + params.demo_bin_dir +  '/demo_server.py &')
    Execute('cp ' + params.demo_bin_dir + '/demo.pid ' + params.demo_pid_file)
      
    
  def status(self, env):
    print 'Status of the Demo Service Master'
    import params
		# Fill me in!
    check_process_status(params.demo_pid_file)
    
  def configure(self, env):
    print 'Writing out configurations'
    import params
    env.set_params(params)
    
    # Write out global.conf
    properties_content=InlineTemplate(params.demo_global_conf_template)
    File(format("{params.demo_conf_dir}/global.conf"), content=properties_content, owner=params.demo_user, group=params.demo_group)
  
  


if __name__ == "__main__":
	Master().execute()
	