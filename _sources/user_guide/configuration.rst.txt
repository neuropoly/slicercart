Configuration
=============

This guide explains how to configure SlicerCART for your specific project needs.

Configuration File
---------------

SlicerCART uses a YAML configuration file to store project settings. The default location is:

.. code-block:: text

   SlicerCART/src/configuration_config.yml

File Structure
------------

The configuration file has the following main sections:

1. **Labels**
   
   Define segmentation labels for your project:

   .. code-block:: yaml

      labels:
        - name: "ICH"
          value: 1
          color: [255, 0, 0]  # RGB values
          description: "Intracerebral hemorrhage"
        - name: "IVH"
          value: 2
          color: [0, 255, 0]
          description: "Intraventricular hemorrhage"

2. **Classification**
   
   Set up classification categories:

   .. code-block:: yaml

      classification:
        categories:
          - name: "Hemorrhage Type"
            options: ["Primary", "Secondary"]
          - name: "Location"
            options: ["Deep", "Lobar", "Mixed"]

3. **Visualization**
   
   Configure display settings:

   .. code-block:: yaml

      visualization:
        window_level: [-20, 180]
        opacity: 0.5
        smoothing: true

Editing Configuration
------------------

There are two ways to edit the configuration:

1. **Using the GUI**
   
   * Click "Edit Configuration" in the module
   * Modify settings in the dialog
   * Save changes

2. **Manual Editing**
   
   * Open configuration_config.yml in a text editor
   * Edit the YAML directly
   * Save the file
   * Restart the module

Configuration Options
------------------

Labels
^^^^^^

Each label requires:

* **name**: Display name
* **value**: Numeric value (1-based)
* **color**: RGB values [0-255]
* **description**: Optional description

Classification
^^^^^^^^^^^^

Categories can have:

* **name**: Category name
* **options**: List of possible values
* **required**: Boolean (true/false)
* **multiple**: Allow multiple selections

Visualization
^^^^^^^^^^^

Available settings:

* **window_level**: Default window/level
* **opacity**: Label opacity
* **smoothing**: Enable smoothing
* **interpolation**: Interpolation method

Advanced Configuration
-------------------

1. **Custom Scripts**
   
   Add custom processing scripts:

   .. code-block:: yaml

      scripts:
        pre_process: "path/to/script.py"
        post_process: "path/to/script.py"

2. **Export Settings**
   
   Configure export formats:

   .. code-block:: yaml

      export:
        format: ["NRRD", "NIFTI"]
        compression: true
        include_metadata: true

3. **Keyboard Shortcuts**
   
   Define custom shortcuts:

   .. code-block:: yaml

      shortcuts:
        next_slice: "Right"
        previous_slice: "Left"
        save: "Ctrl+S"

Best Practices
------------

1. **Version Control**
   
   * Keep configuration under version control
   * Document changes
   * Use descriptive comments

2. **Validation**
   
   * Test configuration changes
   * Verify label values
   * Check color conflicts

3. **Documentation**
   
   * Document custom settings
   * Explain project-specific choices
   * Share with team members

Troubleshooting
-------------

Common Issues
^^^^^^^^^^^

1. **Invalid YAML**
   
   * Check syntax
   * Verify indentation
   * Use YAML validator

2. **Missing Values**
   
   * Ensure required fields
   * Check data types
   * Verify paths

3. **Conflicts**
   
   * Check label values
   * Verify unique names
   * Review color choices 