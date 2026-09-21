Setup Gen3SchemaDev
====================

These instructions assume that you are using macOS with Homebrew installed
and Zsh as your shell. Install Python first, then choose either the package
installation or the source installation with Poetry.

Install Python
--------------

In this tutorial we are using ``Python 3.13.15``.

.. note::

   On macOS, ensure that the full Xcode toolchain is available before building
   Python from source. This is not required when a compatible Python version
   is already installed.

   Install Xcode from the App Store, then select it:

   .. code-block:: bash

      sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
      xcodebuild -version

   If ``pyenv install`` fails while compiling Python, force the Xcode toolchain
   for the current shell and retry:

   .. code-block:: bash

      export PATH="/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
      export CC="$(xcrun --find clang)"
      export CXX="$(xcrun --find clang++)"
      export SDKROOT="$(xcrun --show-sdk-path)"
      export CPPFLAGS="-isysroot $SDKROOT"
      export CFLAGS="-isysroot $SDKROOT"
      export LDFLAGS="-isysroot $SDKROOT"

   For Windows it is recommend to install the linux subsystem.

Install pyenv:

.. code-block:: bash

   brew install pyenv

Add the following lines to ``~/.zshrc`` once, following the
`pyenv setup instructions <https://github.com/pyenv/pyenv#zsh>`_:

.. code-block:: bash

   export PYENV_ROOT="$HOME/.pyenv"
   [[ -d "$PYENV_ROOT/bin" ]] && export PATH="$PYENV_ROOT/bin:$PATH"
   eval "$(pyenv init - zsh)"

Reload your shell configuration, install Python, and select it as your default:

.. code-block:: bash

   source ~/.zshrc
   
   pyenv install -s 3.13.15
   pyenv global 3.13.15
   pyenv rehash

   pyenv which python
   python --version

The first Python path should be the pyenv shim, similar to
``/Users/your-user/.pyenv/shims/python``. If ``pyenv which python`` returns a
path under ``~/.pyenv/versions/3.13.15`` but ``python`` is still not found,
initialize pyenv again in the current shell:

.. code-block:: bash

   export PATH="$HOME/.pyenv/shims:$HOME/.pyenv/bin:$PATH"
   eval "$(pyenv init - zsh)"
   pyenv rehash
   python --version

.. note::

   If your terminal prompt shows an active Conda environment such as ``(base)``,
   deactivate it before checking Python so that Conda does not override pyenv:

   .. code-block:: bash

      conda deactivate
      python --version


Install Gen3SchemaDev
-----------------------------

In your data dictionary project directory, create an isolated environment
and install Gen3SchemaDev:

.. code-block:: bash

   python -m venv .venv
   source .venv/bin/activate
   python -m pip install gen3schemadev
   gen3schemadev --version

Activate pyenv and the Python environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For subsequent sessions, from the data dictionary project directory, activate
pyenv first, then activate the Python virtual environment:

.. code-block:: bash

   source ~/.zshrc
   source .venv/bin/activate

