Setup Gen3SchemaDev
====================

These instructions use the existing ``~/.gen3-local-tools`` Python
environment. Do not create a project-local virtual environment or change your
global Python selection for this tutorial.

Activate the shared environment
-------------------------------

In each new terminal session, activate the environment:

.. code-block:: bash

   source "$HOME/.gen3-local-tools/bin/activate"

Confirm that the active Python comes from the shared environment:

.. code-block:: bash

   python --version
   python -m pip --version

Install Gen3SchemaDev
-----------------------------

Install Gen3SchemaDev into the active shared environment:

.. code-block:: bash

   source "$HOME/.gen3-local-tools/bin/activate"
   python -m pip install gen3schemadev
   gen3schemadev --version

Activate the Python environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For subsequent sessions, activate the shared environment:

.. code-block:: bash

   source "$HOME/.gen3-local-tools/bin/activate"

