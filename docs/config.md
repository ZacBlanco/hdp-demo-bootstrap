[Back to Index](README.md)

# Config

`config.py` is a module which contains some methods to make reading configuration files easy.

--------

## Methods

### `Ambari.read_config(config_file)`

This method retrieves and reads a configuration file `conf` directory and returns an embedded dictionary object where all of the key-value pairs are stored

[See more on the configuration file format in the python docs](https://docs.python.org/2/library/configparser.html)

A typical configuration file has the following format:

	[SECTION HEADER 1]
	key1=value1
	key2=value2
	
	[SECTION HEADER 2]
	key3=value3
	key4=value4
	
	....
	
Using the `read_config` method you can use the object to access the values via the section header and then the key name

Example:

	conf = config.read_config(filename)
	
	conf['SECTION HEADER 1']['key1'] # Now holds value1
	conf['SECTION HEADER 2']['key4'] # Now holds value4
	
### `config.get_conf_dir()`

This method will search for a directory named `conf` in the local directory structure. It will return the path to this directory. 

The method is used when searching for a configuration file in the `read_config` method. However, it may be used outside of the `config` module if other modules utilize the `conf` directory.


### `Ambari.get_config()`

This method retrieves and reads a all **XML files** stored in the `configurations` directory and returns an embedded dictionary object where all of the key-value pairs are stored in the form below:

	conf = config.get_config()
	conf['configurations']['FILENAME']['PROPERTY_NAME'] = PROPERTY_VALUE


i.e. if we had the file `service-config.xml` then we would access it's properties via:

	conf['configurations']['service-config']


### `Ambari.read_xml_config(config_file)`

This method retrieves and reads a configuration file `configurations` directory and returns a  dictionary object where all of the key-value pairs are stored
	
	conf = config.read_xml_config(FILE_PATH)
	conf['PROPERTY_NAME'] = PROPERTY_VALUE

The file format of the XML should follow the following scheme:

	<configuration>
		<property>
			<name>prop1</name>
			<values>val1</value>
			<description></description>
		</property>
		
		<property>
			<name>prop2</name>
			<values>val2</value>
			<description></description>
		</property>
		
More information on this format can be found in the [quickstart guide](README.md#configuration-files)
		
