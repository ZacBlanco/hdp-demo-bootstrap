import sys



def install():
	print('installing')
	
	
	
	pass

def start():
	print('uninstall')
	pass


usage = """
usage: python demo.py [-h]|{install|start|stop|restart}
"""

help_text = """

Use this script to install/start/stop/restart any demo services or scripts on the local machine

-h          
	Shows this help text. Must always be first argument. You can combine it with any other command to get the help text for that command as well.

install     
	Installs necessary functions and components to the current host. This behavior is defined by the user in the install() function.

start		
	Starts the demo services. User defined due to dependency on the demo. If using Ambari service this command may not be implemented

stop        
	Stops the demo services. User defined due to dependency on the demo. If using Ambari service this command may not be implemented

restart     
	Stops the demo and then starts the demo services. This command may perform no function if start() and stop() are not implemented
""" 

accepted_args = ['-h', 'install', 'start', 'stop', 'restart']

help_dict = {
	"install": "Installs necessary functions and components to the current host. This behavior is defined by the user in the install() function.",
	"start": "Starts the demo services. User defined due to dependency on the demo. If using Ambari service this command may not be implemented",
	"stop": "Stops the demo services. User defined due to dependency on the demo. If using Ambari service this command may not be implemented",
	"restart": "Stops the demo and then starts the demo services. This command may perform no function if start() and stop() are not implemented"
}

if len(sys.argv) > 1:
	args = sys.argv[1:]

	if args[0] == '-h' and len(args) > 1:
		print(args[1] + '\n\t\t' + help_dict[args[1]])
	elif args[0] == '-h':
		print(help_text)
	elif len(args) > 0:
		a = args
		if 'install' in a:
			install()
		elif 'start' in a:
			start()
		elif 'stop' in a:
			stop()
		elif 'restart' in a:
			restart()
		else:
			print(usage)
	else:
		print(usage)
else:
	print(usage)

		