# Documentation

The documentation for this project is currently hosted through GitHub pages. The site can be found at [http://blanco.io/hdp-demo-bootstrap](http://blanco.io/hdp-demo-bootstrap/).

Docs for the site are built manually on the `gh-pages` branch. In order to update the docs you need to rebuild and commit the new set of docs to that branch.

The Makefile is set up to push the docs to the root directory of the repository so the build commands for your local version of the docs and the hosted version are still the same.

## Building the Documentation

The documentation for this project is built using sphinx, sphinx-autodoc, and sphinx-apidoc. This allows us to generate documentation directly from the docstrings within our python files.

### Pre-Requisites

- python
- pip (The python package manager, like npm for node.js)
- sphinx (`pip install sphinx`)

To build the documentation (into HTML files), run the following command:

    cd docs/
    make clean
    sphinx-apidoc -e -f -o ./source/autodoc/demo_utils ../demo_utils/demo_utils
    sphinx-apidoc -e -f -o ./source/autodoc/demo_app ../demo_app
    make html
    
Or if you like one-liners (make sure you're in the docs directory):

    make clean; sphinx-apidoc -e -f -o ./source/autodoc/demo_utils ../demo_utils/demo_utils; sphinx-apidoc -e -f -o ./source/autodoc/demo_app ../demo_app; make html

**Important Note**

As of writing this (08/13/2016) the sphinx module throws an error when trying to generate documentation for `demo_server.py`. This is a bug in sphinx when generating docs for flask modules.

A fix is committed but has not yet been released in sphinx. The current workaround is to install the latest stable dev version of sphinx using the following command:

    pip install git+https://github.com/sphinx-doc/sphinx@stable


