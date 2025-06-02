Class Organization
=================

This page shows the class organization diagram of SlicerCART. The diagram is automatically generated using `pyreverse`.

To regenerate this diagram, run the following command from the src subfolder of
the repository:

.. code-block:: bash

   # Install pylint if not already installed
   pip install pylint

   # Generate the class diagram
   pyreverse -o dot -p SlicerCART slicerCART.py
   pyreverse -o dot -p Scripts scripts/*.py
   pyreverse -o dot -p Utils utils/*.py

   python combine_dot_files.py classes_Scripts.dot classes_SlicerCART.dot classes_Utils.dot

   dot -Tpng classes_SlicerCART.dot -o ../docs/_static/images/class_diagram.png

This will create a new class diagram in the `docs/_static/images` directory. The options used are:

.. image:: _static/images/classes.png
   :alt: Class Organization Diagram
   :width: 100%
