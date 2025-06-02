Developer Guide
=======================

Thank you for your interest in contributing to SlicerCART! This document provides guidelines and instructions for contributing to the project.

Code of Conduct
-------------

We are committed to providing a friendly, safe, and welcoming environment for all contributors. Please be respectful and constructive in your interactions.

Coding Standards
-------------

* Max 80 columns for a single code line
* This project uses the `PEP8 <https://peps.python.org/pep-0008/>`_ convention for naming. Reminder:

  - ``MyClass`` for naming a **Class**
  - ``MY_CONSTANT`` for naming a **CONSTANT**
  - ``my_variable`` for naming a **variable**
  - ``define_my_function()`` for naming a **function** (always start with an action verb)
  - Function definition example (add docstrings for explanations):

    .. code-block:: python

       def my_function(arg1):
           """
           Add such a descriptive comment at the beginning of each function
           in order to explain clearly to the next user what the function does. :)

            Args
                arg1: first argument
            """

  - Use ``TODO:`` for naming **To Dos** in the code
  - Add **one blank line** between each function for clarity
  - **Useful comments** are strongly encouraged
  - Want to report a feature improvement or bug? Go on `SlicerCART Github
  <https://github.com/neuropoly/slicer-manual-annotation/issues>`__.

* On Github, 1 issue for 1 Pull Request. Always create a branch.
   .. code-block:: bash

         git checkout -b 'feature-name'

Core Organization
-----------------

See :doc:`repository_organization` for the repository files and folders tree structure.
See :doc:`class_organization` for the class diagrams of the repository scripts.



.. toctree::
   :hidden:

   repository_organization
   class_organization

Development Workflow
-----------------

1. **Make Your Changes**
   
   * Write clean, readable code
   * Follow our coding standards
   * Add tests for new features
   * Update documentation as needed

2. **Test Your Changes**
   
   * Run the test suite
   * Test manually in 3D Slicer
   * Check for any regressions

3. **Commit Your Changes**
   
   * Write clear commit messages
   * Keep commits focused and atomic
   * Reference issues if applicable

4. **Submit a Pull Request**
   
   * Push your changes to your fork
   * Create a pull request from your branch
   * Describe your changes in detail
   * Link to any related issues

Pull Request Guidelines
--------------------

1. **Before Submitting**
   
   * Rebase on latest upstream changes
   * Resolve any conflicts
   * Run all tests
   * Update documentation

2. **PR Description**
   
   * Clearly describe the changes
   * Explain the motivation
   * List any breaking changes
   * Include screenshots if relevant

3. **Review Process**
   
   * Address reviewer comments
   * Make requested changes
   * Keep the discussion constructive


Useful links
----------

  - `PEP8 style guide official documentation <https://peps.python.org/pep-0008/>`_
  - `Polytechnique Montreal Home-Made Guide for programming style (in French) <https://github.com/INF1007-Gabarits/Guide-codage-python>`_


Getting Help
----------

If you need help:

* Join our discussions on GitHub
* Ask questions in issues
* Contact the maintainers

Thank you for contributing to SlicerCART! 