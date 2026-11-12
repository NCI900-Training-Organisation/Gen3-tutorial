Install the Gen3 Python SDK
===========================

This guide installs the Gen3 Python SDK into the repository's existing shared
Python environment at ``~/.gen3-local-tools/``. The same environment is used for the
deployment tools, Gen3SchemaDev, documentation tools, and SDK examples. Do not
create a separate environment for the SDK.

Activate the shared environment
-------------------------------

Activate the existing environment. Do this in every new terminal session:

.. code-block:: console

	python3 -m venv "$HOME/.gen3-local-tools"
	source "$HOME/.gen3-local-tools/bin/activate"
	python -m pip install --upgrade pip

Install the SDK package into that active environment:

.. code-block:: console
	
	python -m pip install gen3
	python -c "from gen3.auth import Gen3Auth; from gen3.file import Gen3File; print('Gen3 SDK is ready')"

In each new terminal, activate ``~/.gen3-local-tools`` before using the SDK.

