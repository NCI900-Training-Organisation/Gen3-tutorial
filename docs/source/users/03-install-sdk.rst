Install the Gen3 Python SDK
===========================

This guide installs the Gen3 Python SDK into the repository's existing shared
Python environment at ``~/.gen3-local-tools/``. The same environment is used for the
deployment tools, Gen3SchemaDev, documentation tools, and SDK examples. Do not
create a separate environment for the SDK.

Activate the shared environment
-------------------------------

Select your operating system below. Windows commands use WSL with Python 3
installed inside WSL. For Linux, install Python 3 and your distribution's
virtual-environment package first. These SDK commands require access to an
existing Gen3 cluster; they do not deploy a local cluster.

Create the shared environment once if it does not exist, then activate it in
every new terminal session:

.. tab-set::
   :sync-group: operating-system

   .. tab-item:: macOS
      :sync: macos

      Use Terminal (Bash or Zsh).

      .. code-block:: console

          python3 -m venv "$HOME/.gen3-local-tools"
          source "$HOME/.gen3-local-tools/bin/activate"
          python -m pip install --upgrade pip


   .. tab-item:: Windows (WSL)
      :sync: windows

      Run these commands in a WSL Bash terminal, with Python and the repository
      inside WSL. Native PowerShell commands are not covered here.

      .. code-block:: console

          python3 -m venv "$HOME/.gen3-local-tools"
          source "$HOME/.gen3-local-tools/bin/activate"
          python -m pip install --upgrade pip


   .. tab-item:: Linux
      :sync: linux

      Use a Bash terminal.

      .. code-block:: console

          python3 -m venv "$HOME/.gen3-local-tools"
          source "$HOME/.gen3-local-tools/bin/activate"
          python -m pip install --upgrade pip


Install the SDK package into that active environment:

.. code-block:: console
	
	python -m pip install gen3
	python -c "from gen3.auth import Gen3Auth; from gen3.file import Gen3File; print('Gen3 SDK is ready')"

In each new terminal, activate ``~/.gen3-local-tools`` before using the SDK.
