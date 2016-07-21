import sys, util
from resource_management import *
from resource_management.core.exceptions import ComponentIsNotRunning
from util.shell import Shell
from util import config
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
	
	
	def install(self, env):
		# Fill me in!
		print 'Install the Demo Service Master';
	
	def stop(self, env):
		# Fill me in!
		print 'Stop the Demo Service Master';
	
	def start(self, env):
		# Fill me in!
		print 'Start the Demo Service Master';
	
	def status(self, env):
		# Fill me in!
		# check_process_status(pid_file)
		print 'Status of the Demo Service Master';
	
	def configure(self, env):
		# Fill me in!
		print 'Configure the Demo Service Master';


if __name__ == "__main__":
	Master().execute()
	