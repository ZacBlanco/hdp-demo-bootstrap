
<div style="text-align:center"><img src="readme-assets/logo.png"></div>
<!--![Logo](readme-assets/logo.png)-->

# Demo Bootstrap [![Python 2.6, 2.7](https://img.shields.io/badge/python-2.6%2C%202.7-orange.svg)](https://docs.python.org/2/) [![Hortonworks Data Platform](https://img.shields.io/badge/Hortonworks-Data%20Platform-brightgreen.svg)](http://hortonworks.com)

> An easy to use framemwork for creating, installing, and running end-to-end demo applications on the Hortonworks Data Platform.

### Demo Utils  [![Build Status](https://img.shields.io/travis/ZacBlanco/hdp-demo-bootstrap.svg?branch=master)](https://travis-ci.org/ZacBlanco/hdp-demo-bootstrap) [![Coverage Status](https://coveralls.io/repos/github/ZacBlanco/hdp-demo-bootstrap/badge.svg?branch=master)](https://coveralls.io/github/ZacBlanco/hdp-demo-bootstrap?branch=master)

This framework hopes to provide a rich set of features including the following:

- Ability to deploy an app to the [Hortonworks Sandbox](http://hortonworks.com/products/sandbox/) or on a multi-node cluster
- Single command Install and Remove via an Ambari Service.
- A simple webapp to display realtime data (via an Ambari view)
- Auto-install HDF
- A built-in webapp skeleton.
- A data generation simulator
- Deployment of pre-made Zeppelin notebooks
- Automatically import NiFi templates
<!--
- Simple Kerberos setup for Sandbox environment*
- Deploy apps on YARN with Slider*
-->

\* = possible feature

## Quick Demo Installation

**Note** Ambari must be installed on your machine for these commands to work.

	
	export VERSION=2.4
	rm -rf /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/DEMOSERVICE
	sudo git clone https://github.com/zacblanco/devicemanagerdemo.git /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/DEMOSERVICE
	git clone https://github.com/ZacBlanco/hdp-demo-bootstrap.git
	cd hdp-demo-bootstrap
	git submodule update --init --recursive
	ambari-server restart
	
	
	export VERSION=2.4
	sed -i s/parallel_execution=0/parallel_execution=1/g /etc/ambari-agent/conf/ambari-agent.ini
	rm -rf /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/DEMOSERVICE
	rm -rf /var/lib/ambari-agent/cache/stacks/HDP/$VERSION/services/DEMOSERVICE
	cp -r /root/devicemanagerdemo /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/DEMOSERVICE
	cp -r /root/devicemanagerdemo /var/lib/ambari-agent/cache/stacks/HDP/$VERSION/services/DEMOSERVICE
	service ambari restart

## Need more Information?

### [Read the docs here!](docs/README.md)
 
### Build the Documentation

Want a local copy of the docs? We've got you covered.

Required:
 - pip
 - sphinx (`pip install sphinx`)
 - [sphinx RTD Theme](https://github.com/snide/sphinx_rtd_theme) (`pip install sphinx_rtd_theme`)

``` sh
cd ./docs
sphinx-apidoc -f -o ./source/  ../demo\_utils/demo\_utils & make html
```