Class Organization
=================

This page shows the class organization diagram of SlicerCART.
The diagram is automatically generated using `pyreverse` (located in the
`docs/_static/images` repository subfolder).

To regenerate this diagram, run the following command from the **src subfolder** of the repository:

.. code-block:: bash

   # Install pylint if not already installed
   pip install pylint

   # Generate the class diagram
   pyreverse -o dot -p SlicerCART slicerCART.py
   pyreverse -o dot -p Scripts scripts/*.py
   pyreverse -o dot -p Utils utils/*.py

   python combine_dot_files.py classes_Scripts.dot classes_SlicerCART.dot classes_Utils.dot

   # Generate both PNG and SVG versions
   dot -Tpng classes_SlicerCART.dot -o ../docs/_static/images/class_diagram.png
   dot -Tsvg classes_SlicerCART.dot -o ../docs/_static/images/class_diagram.svg

.. image:: _static/images/class_diagram.png
   :alt: Classes Diagrams

.. note::
   You can interact with the diagram above by doing mouse right click -> Open in a new tab -> zoom/unzoom to read its content.

This diagram was last updated on |today|.