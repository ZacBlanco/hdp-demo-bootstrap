#!/usr/bin/env python

import os, sys, demo_utils
from demo_utils.shell import Shell

usage = """
Usage: python demo.py {install|pre|service|post}

install:
		Full installation. Runs the pre-install, service-install, then post-install.

pre:
		Run only the pre-service install function

service:
		Runs only the service install (possibly fails if pre-install isn't run)
		
post:
		Runs just the post-service install function
"""

# DEMO.py
# Fill in the pre-install and post-install functions as necessary.

def pre_install():
	# [OPTIONAL]
	# This method should contain any requests to the Ambari server - before installing the demo service

def post_install():
	print("post install function")
	# [OPTIONAL]
	# This method is used for any cleanup/tests/post-install actions that you want to run after the demo Ambari service is installed
	pass

def install_service():
	print("Install here...")
#	export VERSION=2.5
#	'cp -r . /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/DEMOSERVICE
#	curl -X POST http://ambari-server:8080/api/v1/cluster/services/DEMOSERVICE
	pass

def setup():
	# Setup actions for the environment
	pass

def run():
	print("Running install lifecycle")
	setup()
	pre_install()
	install_service()
	post_install()
	print("Done Install")



args = sys.argv[1:]
arg = ""
if not len(args) == 1:
	print(usage)
else:
	arg = args[0]

setup()

if arg == "install":
	run()
elif arg == "pre":
	pre_install()
elif arg == "service":
	install_service()
elif arg == "post":
	post_install()





























	