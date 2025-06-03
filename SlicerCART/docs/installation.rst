Installation
============

This guide will help you install SlicerCART and set up your environment.

Prerequisites
------------

1. **3D Slicer**
   
   SlicerCART is a module for 3D Slicer. You need to have 3D Slicer installed on your system:

   * Download 3D Slicer from the `official website <https://download.slicer.org/>`_ (version 5.6.2 on macOS is recommended)
   * Launch 3D Slicer to verify the installation


2. **Qt**
    The open-source version of Qt can be downloaded from `https://www.qt
    .io/offline-installers <https://www.qt.io/offline-installers>`_ (the version under Qt Creator). **Note:** This package is essential for enabling pop-up windows

3. **Python Dependencies**

   SlicerCART requires several Python packages that will be automatically installed in 3D Slicer python console at module initial launching.

Installation
------------

1. **Get Access to SlicerCART repository**

   * Download `SlicerCART repository as a ZIP file <https://github.com/neuropoly/slicercart/archive/refs/heads/main.zip>`_, and extract the folder to your choice location

   OR

   * Clone the repository to the location of your choice:

     .. code-block:: bash

        # Clone the repository
        git clone https://github.com/neuropoly/slicercart.git

2. **Get Access to SlicerCART in 3D Slicer**

   * Open 3D Slicer

   * Go to Edit -> Application Settings -> Developer. Check `Enable developer mode`

     .. image:: _static/images/developer_mode.png
        :alt: Example Restart
        :align: center
        :height: 100px

   * Go to Edit -> Application Settings

        * On MacOS -> Go to the location of the python file ``SlicerCART.py`` (You should only have one FILE of that name. Note that if you add the path of the FOLDER SlicerCART, it will not work: you MUST add the path of ``SlicerCART.py`` FILE)

          .. image:: _static/images/module_path_adding.png
             :alt: Select Filepath Module
             :align: center

          .. image:: _static/images/module_filepath.png
             :alt: Select and Restart
             :align: center

   * 3D Slicer will ask to Restart: click Ok.

        .. image:: _static/images/example_restart.png
          :alt: Example Restart
          :align: center
          :height: 250px

   * Go to Modules Drop Down -> Examples -> SlicerCART

     .. image:: _static/images/example_slicercart.png
        :alt: Example SlicerCART
        :align: center
        :height: 400px

   * (Optional) Ensure SlicerCART is launched at 3D Slicer startup.

     * To do so, go to `Edit -> Application Settings -> Modules -> Default startup module`


N.B. There might be errors in the Python Console: if so, it is highly
recommended for you to fix them before any further use.


Verification
------------

To verify that SlicerCART is installed correctly:

1. Launch 3D Slicer
2. Go to Modules dropdown menu
3. Look for "SlicerCART" in the list
4. Click on SlicerCART to open the module
5. The module interface should appear in the main panel

Troubleshooting
------------

Common Issues
^^^^^^^^^^^

1. **Module Not Found**
   
   * Verify that 3D Slicer is properly installed
   * Check if the module path is correctly set
   * Try restarting 3D Slicer

2. **Version Compatibility**
   
   * Ensure you're using a compatible version of 3D Slicer (e.g. 5.6.2)
   * Ensure you're using a compatible operating system (e.g. mac OS)

Getting Help
^^^^^^^^^^

If you encounter issues:

* Check our `GitHub Issues <https://github.com/neuropoly/slicercart/issues>`_
* Create a new issue with detailed information about your problem
* Contact the development team 
