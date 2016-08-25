<!--

<div style="text-align:center"><img src="readme-assets/logo.png"></div>
![Logo](readme-assets/logo.png)
-->
# Demo Bootstrap [![Python 2.6, 2.7](https://img.shields.io/badge/python-2.6%2C%202.7-orange.svg)](https://docs.python.org/2/) [![Hortonworks Data Platform](https://img.shields.io/badge/Hortonworks-Data%20Platform-brightgreen.svg)](http://hortonworks.com)

### Demo Utils  [![Build Status](https://img.shields.io/travis/ZacBlanco/hdp-demo-bootstrap.svg?branch=master)](https://travis-ci.org/ZacBlanco/hdp-demo-bootstrap) [![Coverage Status](https://coveralls.io/repos/github/ZacBlanco/hdp-demo-bootstrap/badge.svg?branch=master)](https://coveralls.io/github/ZacBlanco/hdp-demo-bootstrap?branch=master)


An easy to use framemwork for creating, installing, and running end-to-end demo applications on the Hortonworks Data Platform.

## Quick Demo Installation

**Note** Ambari must be installed on your machine for these commands to work.

    export VERSION=2.5
    rm -rf /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/DEMOSERVICE
    sudo git clone https://github.com/zacblanco/hdp-demo-bootstrap.git /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/DEMOSERVICE
    cd /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/DEMOSERVICE
    git submodule update --init --recursive
    ambari-server restart
  
Then head into the Ambari UI and add the HDP Demo Service

## Need more Information?

### [Read The Docs!](docs/README.md)
 
### Build the Documentation

Want a local copy of the docs? We've got you covered.

Required:
 - pip
 - sphinx (`pip install sphinx`)
 - [sphinx RTD Theme](https://github.com/snide/sphinx_rtd_theme) (`pip install sphinx_rtd_theme`)

``` sh
cd ./docs
make clean; sphinx-apidoc -e -f -o ./source/autodoc/demo_utils ../demo_utils/demo_utils; sphinx-apidoc -e -f -o ./source/autodoc/demo_app ../demo_app; make html
```