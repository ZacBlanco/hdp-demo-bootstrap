
# Docs: Index

- [Quick-Start Guide](#quick-start-guide)
- [User Guide](user-guide.md)
- `demo_utils` Modules
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
  
The easiest way to get started creating a demo is to head to the `package/scripts` folder and open up `master.py`

You should find 4 functions

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
  
Once these functions have all been implemented you can simply install the demo service on the Ambari machine by using the `demo.py` file. This will restart Ambari and install your service automatically.

```sh
python demo.py install
```

Another option to install manually is to move the demo repository to the ambari services directory and then restart ambari server. From there you can install it through the Ambari UI:

	cp -r ~/my-demo-location /var/lib/ambari-server/resources/stacks/HDP/2.4/services/DEMOSERVICE
	ambari-server restart


If you need to do anything **before or after installing** the demo, you can implement the `pre_install` and `post_install` methods inside of `demo.py`.  
  - This is useful in cases where you might need to add tasks to the Ambari task queue such as the starting and stopping of services.
  


