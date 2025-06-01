Installation
============

This guide will help you install SlicerCART and set up your environment.

Prerequisites
------------

1. **3D Slicer**
   
   SlicerCART is a module for 3D Slicer. You need to have 3D Slicer installed on your system:

   * Download 3D Slicer from the `official website <https://download.slicer.org/>`_
   * Install the version appropriate for your operating system
   * Launch 3D Slicer to verify the installation

2. **Python Dependencies**
   
   SlicerCART requires several Python packages. These will be installed automatically when you install the module.

Installation Methods
------------------

There are two ways to install SlicerCART:

1. **Using 3D Slicer Extension Manager (Recommended)**
   
   * Open 3D Slicer
   * Go to View -> Extension Manager
   * Search for "SlicerCART"
   * Click Install
   * Restart 3D Slicer when prompted

2. **Manual Installation (For Developers)**
   
   If you want to install from source:

   .. code-block:: bash

      # Clone the repository
      git clone https://github.com/neuropoly/slicercart.git
      cd slicercart

      # Install dependencies
      pip install -r requirements.txt

      # Add the module to 3D Slicer's module path
      # Replace with your Slicer installation path
      export SLICERCART_PATH=/path/to/slicercart
      echo "Add $SLICERCART_PATH to 3D Slicer's additional module paths"

Verifying Installation
--------------------

To verify that SlicerCART is installed correctly:

1. Launch 3D Slicer
2. Go to Modules dropdown menu
3. Look for "SlicerCART" in the list
4. Click on SlicerCART to open the module
5. The module interface should appear in the main panel

Troubleshooting
-------------

Common Issues
^^^^^^^^^^^

1. **Module Not Found**
   
   * Verify that 3D Slicer is properly installed
   * Check if the module path is correctly set
   * Try restarting 3D Slicer

2. **Missing Dependencies**
   
   * Open Python Console in 3D Slicer
   * Try importing required packages
   * Install any missing dependencies

3. **Version Compatibility**
   
   * Ensure you're using a compatible version of 3D Slicer
   * Check the module's version requirements

Getting Help
^^^^^^^^^^

If you encounter issues:

* Check our `GitHub Issues <https://github.com/neuropoly/slicercart/issues>`_
* Create a new issue with detailed information about your problem
* Contact the development team 