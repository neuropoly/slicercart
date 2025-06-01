Architecture
============

This document describes the architecture of SlicerCART, including its main components and their interactions.

Component Overview
----------------

SlicerCART is organized into several main components:

1. **Core Module** (``SlicerCART.py``)
   - Main module class
   - Widget class for UI
   - Logic class for processing

2. **Utilities** (``utils/``)
   - Configuration management
   - Path handling
   - UI theme management
   - Debugging helpers

3. **Scripts** (``scripts/``)
   - Window management
   - Custom interactions
   - Testing

Class Diagram
------------

.. mermaid::

   classDiagram
      class SlicerCART {
          +parent
          +title
          +categories
          +dependencies
          +contributors
          +helpText
          +acknowledgementText
          +__init__(parent)
      }
      class SlicerCARTWidget {
          +logic
          +_parameterNode
          +_updatingGUIFromParameterNode
          +predictions_names
          +called
          +called_onLoadSegmentation
          +config_yaml
          +DefaultDir
          +theme
          +foreground
          +__init__(parent)
          +setup()
          +setupCheckboxes()
          +setupComboboxes()
          +setupFreeText()
          +onSelectVolumesFolderButton()
          +onSaveSegmentationButton()
          +onLoadSegmentation()
          +onLoadClassification()
      }
      class SlicerCARTLogic {
          +__init__()
          +process()
          +run()
      }
      class ConfigPath {
          +DEFAULT_VOLUMES_DIRECTORY
          +create_temp_file()
          +open_project_config_file()
          +get_config_path()
      }
      class UserPath {
          +get_user_path()
          +set_user_path()
          +validate_path()
      }
      class Timer {
          +start()
          +stop()
          +reset()
          +update()
      }
      class LoadSegmentationWindow {
          +setup()
          +show()
          +close()
      }
      class LoadClassificationWindow {
          +setup()
          +show()
          +close()
      }
      class CompareSegmentVersionsWindow {
          +setup()
          +show()
          +close()
      }

      SlicerCART --|> ScriptedLoadableModule
      SlicerCARTWidget --|> ScriptedLoadableModuleWidget
      SlicerCARTLogic --|> ScriptedLoadableModuleLogic
      SlicerCARTWidget ..> Timer : uses
      SlicerCARTWidget ..> ConfigPath : uses
      SlicerCARTWidget ..> UserPath : uses
      SlicerCARTWidget ..> LoadSegmentationWindow : creates
      SlicerCARTWidget ..> LoadClassificationWindow : creates
      SlicerCARTWidget ..> CompareSegmentVersionsWindow : creates

Module Dependencies
-----------------

The module has the following key dependencies:

1. **3D Slicer Core**
   - VTK for visualization
   - Qt for UI
   - CTK for widgets

2. **Python Libraries**
   - NumPy for numerical operations
   - pandas for data management
   - PyYAML for configuration

Data Flow
--------

1. **Configuration Loading**
   - Read project configuration from YAML
   - Set up UI based on configuration
   - Initialize data structures

2. **Image Loading**
   - User selects volume folder
   - Images loaded through Slicer
   - Metadata extracted

3. **Segmentation**
   - User creates/edits segments
   - Segments saved as NRRD/NIFTI
   - Version control maintained

4. **Classification**
   - User adds classifications
   - Data saved in CSV format
   - Multiple versions supported

Directory Structure
-----------------

.. code-block:: text

   SlicerCART/
   ├── src/
   │   ├── SlicerCART.py
   │   ├── utils/
   │   │   ├── ConfigPath.py
   │   │   ├── UserPath.py
   │   │   ├── UITheme.py
   │   │   └── ...
   │   ├── scripts/
   │   │   ├── InteractingClasses.py
   │   │   ├── Timer.py
   │   │   ├── LoadSegmentationWindow.py
   │   │   └── ...
   │   └── Resources/
   │       └── Icons/
   ├── documentation/
   └── tests/ 