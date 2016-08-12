Ambari Customization
====================

Ambari Service Metainfo
----------------------

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




Data Generator
==============


WebSockets Behavior
===================


HTTP Endpoints
==============
