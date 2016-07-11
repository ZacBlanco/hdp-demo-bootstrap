import sys, util
from resource_management import *
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
		print 'Install the Sample Srv Master';
	
	def stop(self, env):
		# Fill me in!
		print 'Stop the Sample Srv Master';
	
	def start(self, env):
		# Fill me in!
		print 'Start the Sample Srv Master';
	
	def status(self, env):
		# Fill me in!
		# check_process_status(pid_file)
		print 'Status of the Sample Srv Master';
	
	def configure(self, env):
		# Fill me in!
		print 'Configure the Sample Srv Master';


if __name__ == "__main__":
	Master().execute()
	