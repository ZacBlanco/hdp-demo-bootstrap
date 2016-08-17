.. HDP demo_utils documentation master file, created by
   sphinx-quickstart on Tue Aug  9 17:56:08 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

HDP Demo Bootstrap Docs
========================

Code Documentation
------------------

.. toctree::
   :maxdepth: 2
   
   autodoc/demo_utils/modules.rst
   autodoc/demo_app/modules.rst
   
Demo Documentation
------------------

.. toctree::
   :maxdepth: 2
   
   user-guide.rst
   customization/modules.rst
   

Indexes
-------

* :ref:`genindex`
* :ref:`modindex`


Need any more help? `Open an issue on GitHub <https://github.com/zacblanco/hdp-demo-bootstrap/issues>`_

Quick-Start Installation Guide
==============================

The main project can be found at https://github.com/zacblanco/hdp-demo-bootstrap

To install this project...

- Open up a shell/terminal on your **Ambari server host machine**
    - You can SSH or if running on the Hortonworks Sandbox open up http://sandbox.hortonworks.com:4200
- Run the following commands

.. code-block:: bash
  :linenos:

  export VERSION=2.4
  rm -rf /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/DEMOSERVICE
  sudo git clone https://github.com/zacblanco/hdp-demo-bootstrap.git /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/DEMOSERVICE
  cd /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/DEMOSERVICE
  git submodule update --init --recursive
  ambari-server restart

This should remove any previous version of the DEMOSERVICE from Ambari and register the new service with the current stack.

+----------+-------------------------------------------------------------------------+
| **Note** | The ``VERSION`` value might change depending on your HDP installation.  |
+----------+-------------------------------------------------------------------------+

+----------+---------------------------------------------------------------------------------------+
| **Note** | If you're working on a VM (i.e HDP Sandbox) you'll need to forward port 7887 and 7888 |
+----------+---------------------------------------------------------------------------------------+

After running these commands you should be able to install the Demo via Ambari's 'Add Service' interface.

After adding the service and starting it, you should be able to access the UI at http://sandbox.hortonworks.com:7887

Troubleshooting
---------------

Common Issues:

If you're having trouble connecting you should first try these things:

- Add following line to your **host machine's** hosts file::

    sandbox.hortonworks.com 127.0.0.1

- Add following line to your **Virtual machine's** hosts file::

    sandbox.hortonworks.com 127.0.0.1

Need any more help? `Open an issue on GitHub <https://github.com/zacblanco/hdp-demo-bootstrap/issues>`_










