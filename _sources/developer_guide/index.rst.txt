Developer Guide
==============

This guide provides detailed information for developers who want to contribute to SlicerCART or understand its internal workings.

.. toctree::
   :maxdepth: 2

   setup
   architecture
   contributing
   coding_style
   testing
   documentation
   deployment

Development Setup
---------------

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/neuropoly/slicercart.git
      cd slicercart

2. Install development dependencies:

   .. code-block:: bash

      pip install -r requirements.txt

3. Set up 3D Slicer development environment

Architecture Overview
------------------

SlicerCART follows a modular architecture with these main components:

* **GUI Layer** - User interface components and event handling
* **Business Logic Layer** - Core functionality and data processing
* **Data Layer** - File I/O and data management
* **Integration Layer** - 3D Slicer integration

Contributing
-----------

We welcome contributions! Please see our :doc:`../contributing` guide for details on:

* Setting up your development environment
* Coding standards
* Pull request process
* Testing requirements

Code Organization
--------------

The codebase is organized as follows:

* ``src/`` - Main source code
* ``utils/`` - Utility functions and helpers
* ``scripts/`` - Helper scripts
* ``Resources/`` - Icons and other resources
* ``documentation/`` - Documentation source files

Testing
-------

We use various testing approaches:

* Unit tests
* Integration tests
* GUI tests
* Manual testing procedures

Documentation
------------

Documentation is written in reStructuredText and built using Sphinx. See the :doc:`documentation` page for details on:

* Writing documentation
* Building documentation locally
* Documentation style guide 