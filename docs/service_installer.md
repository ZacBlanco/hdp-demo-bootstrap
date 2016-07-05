[Back to Index](README.md)

# Service Installer

This module takes the role of setting up some Ambari services that aren't always included in deployments of HDP<=2.4.

This module provides functions to add NiFi and Zeppelin as services to a pre-existing cluster.

It is also possible to use this module to install the `hdp-select` package. (It is necessary when installing the NiFi or Zeppelin services)

The two services are currently 'pre-packaged' as git submodules as a part of this repository under `ambari-services/` directory.

You can also add templates or Pre-made notebooks to add to these installations which will be automatically imported after installing the services.

## Methods

### `service_installer.install_hdp_select()`

This command will attempt to install the `hdp-select` package on the current operating system. The package can only be installed if the system is running Ubuntu12/14 or CentOS6/7.

### `service_installer.is_hdp_select_installed()`

This function will return `True` or `False` whether or not the package `hdp-select` is installed on the current system. This is determined by running the command `which hdp-select`.

An empty response denotes the package is not installed - thus returning `False`. A response which is not empty is interpreted as being a path to the executable which exists, thus returning `True`

### `service_installer.is_ambari_installed()`

This function will return `True` or `False` whether or not the package `ambari-server` is installed on the current system. This is determined by running the command `which ambari-server`.

An empty response denotes the package is not installed - thus returning `False`. A response which is not empty is interpreted as being a path to the executable which exists, thus returning `True`

### `service_installer.add_zeppelin_notebooks()`

This function will attempt to POST all notebooks found under `conf/zeppelin/notes` to an instance of the Apache Zeppelin server via the Notebook API.

The installation configuration details should be made available in the `conf/service-installer.conf` file under the section `ZEPPELIN`. 

##### Required Configuration Options

- protocol
- server
- port

	[ZEPPELIN]
	protocol=http
	server=sandbox.hortonworks.com
	port=9995

### `service_installer.post_notebook(notebook_path)`

Given a path to a JSON notebook file this function will attempt to POST the file to the Zeppelin instance specified by the parameters in the configuration file `conf/service-installer.conf`

### `service_installer.add_nifi_templates()`

This function will attempt to POST all XML templates found under `conf/nifi/templates` to an instance of the Apache NiFi server via the NiFi API.

The installation configuration details should be made available in the `conf/service-installer.conf` file under the section `NIFI`. 

##### Required Configuration Options

- protocol
- server
- port

	[NIFI]
	protocol=http
	server=sandbox.hortonworks.com
	port=9090

### `service_installer.post_template(template_path)`

Given a path to a XML NiFi template this function will attempt to POST the file to the NiFi instance specified by the parameters in the configuration file `conf/service-installer.conf`

### `service_installer.install_zeppelin()`

This function will attempt to install Apache Zeppelin to the Ambari instance on the local machine. The service will add itself to the stack but the **user must manually install and start the service in Ambari**. The program will wait for user to confirm that they have installed the service before continuing.

After installation is successful the function will do a check against the Ambari instance to make sure the service is present in requests to the API. The parameters for the requests are in `global.conf`.

	[AMBARI]
	server=localhost
	port=8080
	username=admin
	password=admin
	cluster_name=Sandbox
	proto=http


### `service_installer.install_nifi()`

This function will attempt to install Apache NiFi to the Ambari instance on the local machine. The service will add itself to the stack but the **user must manually install and start the service in Ambari**. The program will wait for user to confirm that they have installed the service before continuing.

After installation is successful the function will do a check against the Ambari instance to make sure the service is present in requests to the API. The parameters for the requests are in `global.conf`.

	[AMBARI]
	server=localhost
	port=8080
	username=admin
	password=admin
	cluster_name=Sandbox
	proto=http

### `service_installer.check_ambari_service_installed()`


This is a function utilized by the `install_nifi` and `install_zeppelin` functions. It is used to determine whether or not an Ambari service is installed to the specified Ambari instance.