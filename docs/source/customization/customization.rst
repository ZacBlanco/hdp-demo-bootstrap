Ambari Customization
====================

Ambari Service Metainfo
-----------------------

To customize the Ambari service (and the way it appears in Ambari) you'll need to modify the ``metainfo.xml``

An example ``metainfo.xml`` is below.

.. code-block:: xml
  :linenos:
  
  <?xml version="1.0"?>
  <metainfo>
      <schemaVersion>2.0</schemaVersion>
      <services>
          <service>
              <name>DEMOSERVICE</name>
              <displayName>HDP Demo</displayName>
              <comment>An Ambari service to manage the demo</comment>
              <version>0.0.1</version>
              <components>
                  <component>
                      <name>DEMO_MASTER</name>
                      <displayName>Demo Master Service</displayName>
                      <category>MASTER</category>
                      <cardinality>1</cardinality>
                      <commandScript>
                          <script>scripts/master.py</script>
                          <scriptType>PYTHON</scriptType>
                          <timeout>600</timeout>
                      </commandScript>
                  </component>
              </components>
              <osSpecifics>
                  <osSpecific>
                      <osFamily>any</osFamily>
                  </osSpecific>
              </osSpecifics>
          </service>
      </services>
  </metainfo>

Below are the values which you can/should modify.

- ``service/name``: The name that we use throughout the filesystem and in Ambari to refer to the service. Make sure that this is something simple. Avoid spaces.

- ``service/displayName``: The name that is displayed on the sidebar in Ambari and throughout the Ambari UI.

- ``service/comment``: A short description of the service that appears when adding the service to Ambari.

- ``component/name``: The name for the service components that we'll run in Ambari. This name is seen throughout the Ambari API.
- ``component/displayName``: The display name for the components found throughout the Ambari UI.

I do not recommend editing other values. However you can find more information on them in the Ambari documentation.

Ambari Service Lifecycle
------------------------

Lifecycle Stages
^^^^^^^^^^^^^^^^
There are 3 lifecycle stages that the service goes through.

- Install
- Start
- Stop


Each of these has a corresponding function inside of ``package/scripts/master.py``

You shouldn't need to modify these functions, but in case you do I would read the comments inside of ``package/scripts/master.py`` and ``package/scripts/params.py`` to see how they work.

- ``install()`` - Download/install any necessary pre-requisite packages. Create directories/folder/users as necessary.s
- ``start()`` - Download/install any necessary pre-requisite packages. Create directories/folder/users as necessary.
- ``stop()`` - Stop whatever process the service is running on using whatever you need


Writing Out Configurations
^^^^^^^^^^^^^^^^^^^^^^^^^^

When starting and installing the service we need to write out the Ambari configuration file to the format that the ``demo_app`` wants to read from. We use a combination of ``params.py`` and ``master.configure()`` in order to write out the configuration.

The actual writing is done using the ``InlineTemplate`` that Ambari provides from its ``resource_management`` library.

.. code-block:: python
  :linenos:
  
  def configure(self, env):
    print 'Writing out configurations'
    import params
    env.set_params(params)

    # Write out global.conf
    properties_content=InlineTemplate(params.demo_global_conf_template)
    File(format("{params.demo_conf_dir}/global.conf"), content=properties_content, owner=params.demo_user, group=params.demo_group)

Any of the ``params.py`` variable names can be used inside the templates' braces (``{{  }}``) to show where a variable value should be inserted when writing the template.


Add Configuration Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^

To add a configuration variable you'll need to do 4 things

1. Add your param name to ``global.conf`` (And reference it wherever needed in the project).
2. Add the property to the ``demo-config.xml`` file with an appropriate name.
3. Add a new variable to ``params.py`` using your Ambari property name you used in (2).
4. Add the param to the ``demo.global.conf`` template *inside* ``demo-config.xml`` using the variable name from (3).


Example:

We have a ``global.conf`` file below:

.. code-block:: ini
  :linenos:
  
  [DEMO]
  server_port=7887
  name=my_demo
  
  
Then in ``demo-config.xml`` we have

.. code-block:: xml
  :linenos:
  
  <configuration supports_final="true">
    <property>
      <name>demo.server.port</name>
      <value>7887</value>
      <description>URL for the Demo. Unused by the demo</description>
    </property>
    <property>
      <name>demo.name</name>
      <value>my_awesome_demo</value>
      <description>Port where you can access the demo user interface (will need to forward on Sandbox VM)</description>
    </property>
    <property>
      <name>demo.global.conf</name>
      <value>
  [DEMO]
  server_port={{ demo_server_port }}
  name={{ demo_name }}
      </value>
      <description>global.conf template</description>
    </property>
  </configuration>


So then Once we have our ``demo-config.xml`` we look in ``params.py``

.. code-block:: python
  :linenos:
  
  import sys, os, pwd, grp, signal, time, glob
  from resource_management import *
  from resource_management.core import shell
  from subprocess import call

  config = Script.get_config()
  
  demo_server_port = config['configurations']['demo-config']['demo.server.port']
  demo_name = config['configurations']['demo-config']['demo.name']


Note how in ``demo-config.xml`` the variable names from ``params.py`` are labeled inside of the configuration template.

Those values will be filled in and then written out upon the ``master.configure()``

You'll also need to **uninstall** and **reinstall** the service to make any updates to the Ambari service configuration. (Or delete the configuration and POST a new one to the API - look in the docs).

Data Generator
==============

Overview
--------

Getting data for demos can be a nuisance. The generator tries to make that easier so we don't have to worry about finding data.

I suggest reading up on the documentation for the generator See the `demo_utils.generator module <../autodoc/demo_utils/demo_utils.generator.html>`_

The generator itself uses JSON for configuration. The basic structure is outlined below.

- The root 'object' itself is a list
- Each item in the list is called a **datum**
    - Each datum has a type name associated with it
    - A datum generates a single piece of data. (think column).
    - At the implementation level, a  each datum is an implementation of ``demo_utils.generator.AbstractDatum``
- Data is generated with ``generator.generate()``
    - This creates an object with key value pairs mapping the ``fieldName`` to the generated value


Lat/Lon Coordinates Example
---------------------------

Below is a JSON config for generating latitude and longitude coordinates.

.. code-block:: json
  :linenos:
  
  [
    {
      "fieldName":    "lat",
      "type":         "decimal",
      "distribution": "uniform",
      "a": 10,
      "b": 20
    },
    {
      "fieldName":    "lon",
      "type":         "decimal",
      "distribution": "uniform",
      "a": 10,
      "b": 20
    }
  ]
  
``"a"`` and ``"b"`` are simply just parameters for the uniform distribution.

They specify that all numbers between ``10`` and ``20`` should be picked with equal probability. They are the standard parameter values for a uniform distribution.

  
Sample Output:

.. code-block:: json
  
  {
    "lat": 15.679044307618824,
    "lon": 17.982797693128596
  }
  
As you can see here the configuration format is easily human-readable and can be extended to a multitude of other things.

Datum Reference
---------------------

+---------------+-------------+--------------------------+
| Datum Name    | Type Name   | Parameters               |
+===============+=============+==========================+
| StringDatum   | ``string``  | ``values``               |
+---------------+-------------+--------------------------+
| IntDatum      | ``int``     | ``distribution``         |
+---------------+-------------+--------------------------+
| DecimalDatum  | ``decimal`` | ``distribution``         |
+---------------+-------------+--------------------------+
| BooleanDatum  | ``boolean`` | ``values`` (optional)    |
+---------------+-------------+--------------------------+
| MapDatum      | ``map``     | ``mapFromField``, ``map``|
+---------------+-------------+--------------------------+

Probabilities of ``values``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

For the ``StringDatum`` specifically, ``values`` can be two types. A list or object.

If ``values`` is a list - then each item in the list has equal probability to be chosen.

If ``values`` is an Object then it should have the following form:

.. code-block:: json
  
  {
    "fieldName": "string_example",
    "type": "string",
    "values" : {
      "value1": 0.1,
      "values2": 0.2,
      "value3": 0.7
    }
  }
  
Each key holds a number between 0 and 1. This corresponds to the probability that each value has of being picked. i.e. ``"value3"`` will appear in 70% of all random data rows

Also note **the probabilities must all sum to** ``1.0``


Types of Distributions
^^^^^^^^^^^^^^^^^^^^^^

For ``int`` and ``decimal`` you must specify a distribution. You may also modify the arguments for the distribution. The defaults are noted below.

- **uniform(a, b)**
    - Defaults
        - `a`: 0
        - `b`: 1
- **exponential(lambda)**
    - Defaults
        - `lambda`: 1
- **gaussian(mu, sigma)**
    - Defaults
        - `mu`: 0
        - `sigma`: 1
- **gamma(alpha, beta)**
    - Defaults
        - `alpha`: 1
        - `beta`: 1


Examples
^^^^^^^^

StringDatum
"""""""""""

The difference between the two fields is that the ``lname`` field is randomly generated via the probablities, rather than equally across the set of values.

.. code-block:: json
  
  [
    {
      "fieldName": "fname",
      "type": "string",
      "values": ["Zac", "John", "Sally", "Mary", "Jane"]
    },
    {
      "fieldName": "lname",
      "type": "string",
      "values": {
        "Doe": 0.5,
        "Smith": 0.1,
        "Jones": 0.2,
        "Williams": 0.2
      }
    }
  ]
  
DecimalDatum
""""""""""""

.. code-block:: json
  
  [
    {
      "fieldName": "a_number",
      "type": "decimal",
      "distribution": "exponential",
      "lambda": 0.21
    }
  ]
  
  
IntDatum
"""""""""""

.. code-block:: json
  
  [
    {
      "fieldName": "another_number",
      "type": "int",
      "distribution": "exponential",
      "lambda": 0.21
    }
  ]
  
BooleanDatum
""""""""""""

The difference between the two fields here is that the values in the 2nd field are generated by probabilities, instead of a 50/50 split. ``True`` appears 7/10 times. ``False`` appears only 3/10 (average)

.. code-block:: json
  
  [
    {
      "fieldName": "5050_bool",
      "type": "boolean"
    },
    {
      "fieldName": "prob_bool",
      "type": "boolean",
      "values": {
        "True": 0.7,
        "False": 0.3
      }
    }
  ]
  

MapDatum
""""""""

.. code-block:: json
  
  [
    {
      "fieldName": "fname",
      "type": "string",
      "values": ["Zac", "John", "Sally", "Mary", "Jane"]
    },
    {
      "fieldName": "lname",
      "type": "string",
      "values": {
        "Doe": 0.5,
        "Smith": 0.1,
        "Jones": 0.2,
        "Williams": 0.2
      }
    },
    {
      "fieldName": "gender",
      "type": "map",
      "mapFromField": "fname",
      "map": {
        "Zac": "M",
        "John": "M",
        "Sally": "F",
        "Mary": "F",
        "Jane": "F"
      }
    }
  ]


WebSockets App
==============


WebSockets 101
--------------

Websockets are awesome because they allow long-lived connections from the server to browser clients in order to continuously send data to or receive data from a server. This allows realtime webpage updates!

Packaged inside our app we have a websocket server. The server implementation is very basic but it allows us to broadcast messages to our clients and get updates from the server in realtime.

To customize this real-time behavior you need to set up functions on the **client** and the **server**


Message Broadcasting
--------------------

If you take a look inside ``demo_app.cluster.WSDemoServer`` you should see a function called ``broacast(data)``

``data`` should be a string object (see documentation).

Inside the flask application you can call ``websocket_server.broadcast('Message to Client')`` and this will send ``'Message to Client'`` to all of the websocket clients.

You could imagine this would be useful for something like updating locations on a map in realtime!

Server-Side
-----------

Inside of ``demo_server.py`` you can find an API endpoint ``/websockets/data``. The code snippet of the function is below.

.. code-block:: python
  :linenos:
  
  @app.route("/websockets/data", methods=['POST'])
  def push_websockets():
    '''Broadcast a message to all Websocket clients

    Route:
      ``POST /websockets/data``

    Returns:
      N/A

    '''
    msg = request.get_json()
    msg = json.dumps(msg)
    ws_app.broadcast(msg)
    return ''
    
What this does is open a RESTful HTTP endpoint where we can POST json data. Each time data is POSTed to the endpoint it will echo that data out (in real-time!) to all of the clients who are connected to the websocket server (``ws_app``). The clients are then responsible for the handling of such data

You can define more functions for when you want to broadcast the data. This is currently the only built-in broadcasting


Client-Side
-----------

On the client side we need to use javascript in our webpage to handle what happens with our websocket connection.

Below is the code from ``demo.js`` where we define the behavior for websocket connections

.. code-block:: javascript
  :linenos:
  
  function demoWebsocket() {
    /* Use this object to define behavior for websocket connections

    To access the data in the message use `ev.data`

    onopen - functionality for when the connection opens
    opclose - funtionality for when the connection closes
    onmessage - the functionality for when the client receives a message from the server
        This is the "meat" of the connection. Most of your logic will probably go here
    onerror - What to do in the event of a connetion error
    */
    var self = this;
    self.connected = false;
    self.url = getWsUrl();

    self.connect = function (url) {
      self.ws = new WebSocket(url);

      /*These function must be set for every new websocket object*/
      self.ws.onopen = function (ev) {
        console.log('Websocket: opened new connection')
        self.connected = true;
        self.updateConnectionStatus(self.connected);


        //Add code below this
      };

      self.ws.onclose = function (ev) {
        console.log('Websocket: closed connection')
        self.connected = false;
        self.updateConnectionStatus(self.connected);


        //Add code below this
      };

      self.ws.onmessage = function (ev) {
        console.log('Websocket: received message')

        //Do stuff with ev.data
        //      console.log(ev.data)


        //      Lat/Lon. Demo for plotting markers
        //      
        //      var data = JSON.parse(ev.data);
        //      for(i = 0; i < data.length; i++) {
        //        lat = data[i].lat
        //        lon = data[i].lon
        //        L.marker([lat, lon]).addTo(map);
        //      }
        //      fmtd = JSON.stringify(JSON.parse(ev.data), null, 2)
        //      self.logSocket("<pre>" + fmtd + "</pre>")
      };

      self.ws.onerror = function (ev) {
        self.connected = false;
        self.logSocket('Error connecting to websocket server')
        self.updateConnectionStatus(self.connected);
      };

      self.checkConnection = function () {
        self.updateConnectionStatus(self.connected);
        if (self.connected == false) {
          self.ws = self.connect(self.url);
        }
      }
      return self.ws
    }

    self.logSocket = function (message) {
      var msg = message + '<br>';
      $('#websocket-console-data').append(msg)
    }

    self.updateConnectionStatus = function (connected) {
      if (connected == true) {
        $('#websocket-connection-status').removeClass().addClass('label label-success connection-label').html('Connected')
      } else if (connected == false) {
        $('#websocket-connection-status').removeClass().addClass('label label-danger  connection-label').html('Disconnected')
      }
    }

    self.ws = self.connect(self.url);


    //Set an interval to check whether or not our socket is connected.
    setInterval(function () {
      self.checkConnection(self.connected)
    }, 5000);

  }
  
  
The key thing to notice here is the ``ws`` WebSocket object and the four (4) functions

- ``onopen``
    - Determine behavior when the connection is first opened
- ``onclose``
    - Determine behavior when the connection is closed or disconnected
- ``onmessage``
    - Determine behavior when a message arrives from the server
- ``onerror``
    - Determine behavior when there is an error connecting or receiving data

Built in to the ``demoWebsocket()`` object you can call a function ``self.logSocket(message)``. This will append a message to the websockets console.

Other than that you can use Jquery and any combination on the Javascript web API to control the webpage. The implementation is currently up to the user.

The Map View
============

We have a nice Map UI, however there aren't any user controlls available other than zooming and scrolling manually.

However because we use leaflet.js we can add more functionality to this map.

Couple leaflet with Websockets and you have a realtime geo-dashboard right at your fingertips.

Below you'll find some short guides on performing function with the map. However, I suggest taking a brief look at the `leaflet quickstart guide <http://leafletjs.com/examples/quick-start.html>`_


Change the Map Default Location
-------------------------------

In order to change the default location that the map loads on you'll need to dive into ``demo_app/static/demo.js``

Look for the line:

.. code-block:: javascript
  
    /* Init Map on the UI */
    var map = initMap([37.4133111, -121.9805886])
    
This line initalizes the map. The arguments here are the coordinate points on the map. Simply replace the coordinates there with your own to change the initial location.


Other functions with the map (like adding markers or areas) can be performed with the leaflet.js library. I would suggest looking into the leaflet documentation or `the quickstart guide <http://leafletjs.com/examples/quick-start.html>`_ on their site



HTTP Endpoints
==============
