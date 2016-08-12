.. HDP demo_utils documentation master file, created by
   sphinx-quickstart on Tue Aug  9 17:56:08 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

HDP Demo Bootstrap Docs
========================

Code Documentation
##################

.. toctree::
   :maxdepth: 2
   
   autodoc/demo_utils/modules.rst
   autodoc/demo_app/modules.rst
   
Demo Documentation
##################

.. toctree::
   :maxdepth: 2
   
   customization/modules.rst

Indexes
-------

* :ref:`genindex`
* :ref:`modindex`


Quick-Start Guide
=================

The main project can be found at <https://github.com/zacblanco/hdp-demo-bootstrap>

To install this project just run the following commands

.. code-block:: bash
  :linenos:

  export VERSION=2.4
  rm -rf /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/DEMOSERVICE
  sudo git clone https://github.com/zacblanco/hdp-demo-bootstrap.git /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/DEMOSERVICE
  cd /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/DEMOSERVICE
  git submodule update --init --recursive
  ambari-server restart

This should remove any previous version of the Demo service from Ambari and register the new service with the current stack.

**Note**: The ``VERSION`` value should change depending on your HDP installation.

After running these commands you should be able to install the Demo via Ambari's 'Add Service' interface.

You can











