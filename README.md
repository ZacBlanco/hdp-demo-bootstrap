
<div style="text-align:center"><img src="readme-assets/logo.png"></div>
<!--![Logo](readme-assets/logo.png)-->

[![Build Status](https://img.shields.io/travis/ZacBlanco/hdp-demo-bootstrap.svg?branch=master)](https://travis-ci.org/ZacBlanco/hdp-demo-bootstrap) [![Coverage Status](https://coveralls.io/repos/github/ZacBlanco/hdp-demo-bootstrap/badge.svg?branch=master)](https://coveralls.io/github/ZacBlanco/hdp-demo-bootstrap?branch=master) [![Python 2.6, 2.7](https://img.shields.io/badge/python-2.6%2C%202.7-orange.svg)](https://docs.python.org/2/) [![Hortonworks Data Platform](https://img.shields.io/badge/Hortonworks-Data%20Platform-brightgreen.svg)](http://hortonworks.com)

# Demo Bootstrap

> An easy to use framemwork for creating, installing, and running end-to-end demo applications on the Hortonworks Data Platform.

This framework hopes to provide a rich set of features including the following:

- Ability to deploy an app to the [Hortonworks Sandbox](http://hortonworks.com/products/sandbox/) or on a multi-node cluster
- Single command Install and Remove via an Ambari Service.
- A simple webapp to display realtime data (via an Ambari view)
- Auto-install HDF
- A built-in webapp skeleton.
- A data generation simulator
- Deployment of pre-made Zeppelin notebooks
- Automatically import NiFi templates
- Simple Kerberos setup for Sandbox environment*
- Deploy apps on YARN with Slider*

\* = possible feature

## Quick Demo Installation

**Note** Ambari must be installed on your machine for these commands to work.

	export VERSION=2.4
	rm -rf /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/DEMO_SERVICE
	sudo git clone https://github.com/zacblanco/hdp-demo-bootstrap.git /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/DEMO_SERVICE
	ambari-server restart

## Need more Information?

### [Read the docs here!](docs/README.md)
 
 