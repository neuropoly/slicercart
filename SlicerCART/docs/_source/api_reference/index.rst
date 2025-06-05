API Reference
============

This section provides detailed API documentation for all the modules and classes in SlicerCART.

.. toctree::
   :maxdepth: 2

   slicercart
   utils
   scripts

Main Module
----------

.. automodule:: SlicerCART.src.SlicerCART
   :members:
   :undoc-members:
   :show-inheritance:

Utility Functions
---------------

.. automodule:: SlicerCART.src.utils
   :members:
   :undoc-members:
   :show-inheritance:

Scripts
-------

.. automodule:: SlicerCART.src.scripts
   :members:
   :undoc-members:
   :show-inheritance:

Class Hierarchy
-------------

.. mermaid::

   classDiagram
      class SlicerCART {
          +__init__(parent)
          +setup()
          +cleanup()
      }
      class SlicerCARTWidget {
          +__init__(parent)
          +setup()
          +cleanup()
          +onSelect()
          +onApply()
      }
      class SlicerCARTLogic {
          +__init__()
          +process()
      }
      SlicerCART --|> ScriptedLoadableModule
      SlicerCARTWidget --|> ScriptedLoadableModuleWidget
      SlicerCARTLogic --|> ScriptedLoadableModuleLogic 