Setup Gen3SchemaDev
====================

These instructions use the existing ``~/.gen3-local-tools`` Python
environment. Do not create a project-local virtual environment or change your
global Python selection for this tutorial.

Activate the shared environment
-------------------------------

In each new terminal session, activate the environment:

.. tab-set::
   :sync-group: operating-system

   .. tab-item:: macOS
      :sync: macos

      Use Terminal (Bash or Zsh).

      .. code-block:: bash

         source "$HOME/.gen3-local-tools/bin/activate"


   .. tab-item:: Windows (WSL)
      :sync: windows

      Run these commands in a WSL Bash terminal, with Python and the repository
      inside WSL. Native PowerShell commands are not covered here.

      .. code-block:: bash

         source "$HOME/.gen3-local-tools/bin/activate"


   .. tab-item:: Linux
      :sync: linux

      Use a Bash terminal.

      .. code-block:: bash

         source "$HOME/.gen3-local-tools/bin/activate"


Confirm that the active Python comes from the shared environment:

.. code-block:: bash

   python --version
   python -m pip --version

Install Gen3SchemaDev
-----------------------------

Install Gen3SchemaDev into the active shared environment:

.. tab-set::
   :sync-group: operating-system

   .. tab-item:: macOS
      :sync: macos

      Use Terminal (Bash or Zsh).

      .. code-block:: bash

         source "$HOME/.gen3-local-tools/bin/activate"
         python -m pip install gen3schemadev
         gen3schemadev --version


   .. tab-item:: Windows (WSL)
      :sync: windows

      Run these commands in a WSL Bash terminal, with Python and the repository
      inside WSL. Native PowerShell commands are not covered here.

      .. code-block:: bash

         source "$HOME/.gen3-local-tools/bin/activate"
         python -m pip install gen3schemadev
         gen3schemadev --version


   .. tab-item:: Linux
      :sync: linux

      Use a Bash terminal.

      .. code-block:: bash

         source "$HOME/.gen3-local-tools/bin/activate"
         python -m pip install gen3schemadev
         gen3schemadev --version


Activate the Python environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For subsequent sessions, activate the shared environment:

.. tab-set::
   :sync-group: operating-system

   .. tab-item:: macOS
      :sync: macos

      Use Terminal (Bash or Zsh).

      .. code-block:: bash

         source "$HOME/.gen3-local-tools/bin/activate"


   .. tab-item:: Windows (WSL)
      :sync: windows

      Run these commands in a WSL Bash terminal, with Python and the repository
      inside WSL. Native PowerShell commands are not covered here.

      .. code-block:: bash

         source "$HOME/.gen3-local-tools/bin/activate"


   .. tab-item:: Linux
      :sync: linux

      Use a Bash terminal.

      .. code-block:: bash

         source "$HOME/.gen3-local-tools/bin/activate"
