
# Docs: Index

- [Quick-Start Guide](#quick-start-guide)
- Modules
  - [ambari.py](ambari.md)
  - [config.py](config.md)
  - [curl_client.py](curl_client.md)
  - [generator.py](generator.md)
  - [service_installer.py](service_installer.md)
  - [shell.py](shell.md)

<a name="quick-start-guide"></a>

# Quick-Start Guide

### Pre-Requisites

- Python 2.6 or 2.7 (3+ may work but isn't tested)
- `pip`, the python package manager installed


In order to get up and running with this framework there are a few important points to remember

- Everything for the demo should be run on the Ambari host machine.
  - This means you should leave plenty of room on your Ambari host for any components or other services that are going to be installed.
- This framework is not a standalone demo.
  - The purpose of this bootstrap is to house a useful set of tools for devs and demo-makers.
  - The tools are designed so that users can worry less about the plumbing of the demo on the machine and more about the _actual_ demo.
- The demo is implemented as an Ambari Service
  - This means everything we do in creating a demo will be accessible via Ambari
  

Let's dive in!

### Implementing the Ambari Service

In order to make this demo work as an Ambari Service we have to implement the same architecture that Ambari expects of all of its services. The aim of this quick-start guide is to provide a a brief explanation on how to properly implement the service. 

More detailed explanations on how to properly implement the service can be found under [Ambari Service Implementation](ambari-service-implementation.md). You can also refer to the Ambari [documentation on custom services](https://cwiki.apache.org/confluence/display/AMBARI/Defining+a+Custom+Stack+and+Services).

Time to dive in!

There are two main items that are addressed in this guide:

1. The architecture of the demo service
2. How to properly implement the demo service

### Architecture

The directory structure is outlined below.

	├── ambari-services
	│   ├── ambari-nifi-service
	│   └── ambari-zeppelin-service
	├── docs
	├── package
	│   ├── configuration
	│   ├── scripts
	│   └── util
	├── readme-assets
	└── tests
		└── res
		
- `ambari-services`
  - This directory houses two git submodules. The Ambari service for Zeppelin and Ambari service for NiFi
- `docs`
  - The docs folder houses all of the markdown documentation such as this file.
- `package`
  - This folder houses the main assets for what will become the custom Demo Ambari Service
  - Inside you find `configuration`, `scripts`, and `util`. 
    - `util` is a custom python package that was designed for this repository. It contains a few modules which are documented above.
	- `scripts` - This is where you'll implement the custom parameters for the demo Ambari service. It contains files `master.py` and `params.py`.
	- `configuration` contains all of the files that pertain to the configuration parameters which are utilized by modules in `util`. Those parameters exposed in the files are configurable via the Ambari service
- `tests`
  - Contains all of the tests for the custom modules in `package/util`

### Configuration Files

Configuration files are defined in XML format. They are the same format used by Ambari. 

Typically they are structured as such:

	
	<?xml version="1.0"?>
	<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
	<configuration supports_final="true">
		<property>
			<name>configuration.property1</name>
			<value>configuration_value_1</value>
			<description> Description of Property (optional) </description>
		</property>
	</configuration>
	
You can define multiple properties inside of each file. They can than be accessed through two different means: `util.config` or `resource_management.libraries.script.script.Script`

(Note that the latter is an Ambari library)

You can other optional parameters inside the `<property>` tags XML files to define constraints on the values

- `<display-name>` - A 'prettier', more human-readable name for the property
- `<values-attributes>`
  - Inside of this tag can go:
  - `<type>` - One of `string`, `value-list`, `float`, `int`, `boolean`
  - `<minimum>` - minimum value allowed
  - `<maximum>` - maximum value allowed
  - `<unit>` - The unit used for the value e.g. MB (Megabytes), Second, Minutes, etc...
  - `<increment-step>` - The minimum amount each increment must be. i.e. min = 0, max = 1000 but we only want to allow multiples of 10, then `increment-step` should be set to 10
  
More information can be found under [Enhanced Configs in the Ambari Wiki](https://cwiki.apache.org/confluence/display/AMBARI/Enhanced+Configs).

Using `util.config` you can simply read a config like the following:

	from util import config
	
	conf = config.get_config()
	prop_value = conf['configurations']['{CONF_FILE_NAME}']['{PROPERTY_NAME}']
	# -- do stuff -- with prop_value

It might be useful to note that unless `type` metadata is available all property values will be interpreted as strings.

### Scripts

#### `master.py`

Under the `package/scripts` directory there is a file named `master.py` this file needs to have certain functions 'filled in' on a per demo basis. These functions define the behavior for the service.

The functions are:

- install()
- start()
- stop()
- status()
- configure()

The main purpose is to set up, start, stop, and restart any demo services. They can be implemented using the Ambari `resource_management` libraries or the custom `util` libraries.

A few notes on these functions

- `configure()` is used to take the Ambari configuration values and write the parameters values out to any component configuration files
  - At the end `install()` you should run `self.configure()`
  - At the beginning of `start()` you should run `self.configure()`
- `status()` - you can use the funtion `check_process_status(pid_file)` to report on the status of your service's process.
  - This will allow Ambari to show the service as running correctly.

#### `params.py`

`params.py` is important because it allows us to define variables for our configuration that can be written to the _actual_ configuration files using `{{variable_name}}`.

Example:

We define a property in `demo-env.xml`

	<property>
		<name>special.property1</name>
		<value>my_property_value</value>
		<description>A special property</description>
	</property>
	<property>
		<name>content</name>
		<value>
		special.property0=999
		special.property1={{special_property1}}
		special.property2=999
		special.property3=999
		special.property4=999
		</value>
		<description>A special property</description>
	</property>
	
Now in `params.py`

	from util import config
	conf = config.get_config()
	demo_env_content = conf['configurations']['demo-env']['content']
	special_property1 = conf['configurations]['demo-env']['special.property']
	
Then in `master.py` you could execute using `InlineTemplate` (A function from `resource_management.core.source`) and File (function from `resource_management.core.resources.system`) to write to a file:

	import params
	demo_env = InlineTemplate(params.demo_env_content)
	File('~/file/location/demo-env.conf',  content=demo_env, owner=your_user, group=your_user_group)


### Util

The `util` package is a custom-built python package which houses a few modules that have been well documented and have many uses when installing an Ambari service. 

You can find documentation on all the `util` modules in the index below

##### List of Modules

- [ambari.py](ambari.md)
- [config.py](config.md)
- [curl_client.py](curl_client.md)
- [generator.py](generator.md)
- [service_installer.py](service_installer.md)
- [shell.py](shell.md)


### `tests`

For this framework we use a python called `nose` to run tests. If you don't have `pip` already you need to obtain it to help manage python modules.

Install via

	pip install nose


This folder contains tests for everything that is in the `util` module. It is run with
[`nosetests`](http://nose.readthedocs.io/en/latest/)

currently a Work-In-Progress. Likely outcomes:

- current tests move from `tests/` to `tests/util`
- New directory `tests/demo-tests` - integration testing for demos with a few 'basic' functionality tests



