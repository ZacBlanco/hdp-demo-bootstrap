import sys, pwd, grp, os
import resource_management
from resource_management import *
from resource_management.core.exceptions import ComponentIsNotRunning
from resource_management.core import shell
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
    
    self.create_linux_user(params.demo_user, params.demo_group)
    self.configure(env)
    print 'Install the Demo Service Master';
    if params.demo_user != 'root':
      Execute('cp /etc/sudoers /etc/sudoers.bak')        
      Execute('echo "' + params.demo_user + '    ALL=(ALL)       NOPASSWD: ALL" >> /etc/sudoers')
    
    demo_logging_dir = os.path.dirname(os.path.realpath(params.demo_logging_log_file))
    
    Execute('mkdir -p '+ params.demo_pid_dir + ' ' + demo_logging_dir)
    Execute('chown -R ' + params.demo_user + ':' + params.demo_group + ' ' + params.demo_pid_dir)
    Execute('chown -R ' + params.demo_user + ':' + params.demo_group + ' ' + demo_logging_dir)
    
    # Ensure pip is instaled
    Execute('sudo yum install python-pip')
    Execute('pip install -r ' + '/'.join([params.demo_bin_dir, 'requirements.txt']))
    Execute('python ' + params.demo_bin_dir +  '/service.py INSTALL')

  def stop(self, env):
    # Fill me in!
    import params
    print 'Stop the Demo Service Master'
    try:
      Execute('kill `cat ' + params.demo_pid_file + '`' )
      Execute('python ' + params.demo_bin_dir +  '/service.py STOP')
    except resource_management.core.exceptions.Fail as e:
      pass

  def start(self, env):
    print 'Start the Demo Service Master'
    import params
    self.configure(env)
    Execute('nohup python ' + params.demo_bin_dir +  '/demo_server.py >/dev/null 2>&1 & echo $! > ' + params.demo_pid_file)
    Execute('python ' + params.demo_bin_dir +  '/service.py START')
    print('Checking process has started')
    print(20 * '-')
    Execute('kill -0 `cat ' + params.demo_pid_file + '`')
    check_process_status(params.demo_pid_file)
    
    
  def status(self, env):
    print 'Status of the Demo Service Master'
    import params
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
  