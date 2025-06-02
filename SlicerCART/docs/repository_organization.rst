Repository Organization
=====================

Below is the repository folder tree organization. To regenerate this tree,
run the following command from the root of the repository:

.. code-block:: bash

   # On macOS/Linux
   tree -I '_build|__pycache__|*.pyc|.git|.DS_Store' > SlicerCART/docs/repository_tree.txt
   
   # On Windows (using PowerShell)
   Get-ChildItem -Recurse | Where-Object { $_.FullName -notmatch ' (_build|__pycache__|\.pyc|\.git|\.DS_Store)' } | ForEach-Object { $_.FullName.Replace($PWD, '') } | Out-File SlicerCART/docs/repository_tree.txt

.. literalinclude:: repository_tree.txt
   :language: text

This documentation was last updated on |today|.