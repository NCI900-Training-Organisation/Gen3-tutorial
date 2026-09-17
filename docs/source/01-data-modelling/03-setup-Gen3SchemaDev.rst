Setup Gen3SchemaDev
====================

These instructions assume that you are using macOS with Homebrew installed
and Zsh as your shell. Install Python first, then choose either the package
installation or the source installation with Poetry.

Install Python
--------------

Before installing Python with pyenv, ensure that the full Xcode toolchain is available on macOS. Without it, pyenv can use the Homebrew LLVM compiler instead of the Apple/Xcode toolchain, and the build can fail during configuration.


.. note::

   For mac, Install Xcode from the App Store, then select it:

   .. code-block:: bash

      sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
      xcodebuild -version

   If the build still prefers the Homebrew clang, force the Xcode toolchain for the current shell before running pyenv:

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
   python --version

If your terminal prompt shows an active Conda environment such as ``(base)``,
deactivate it before checking Python so that Conda does not override the pyenv
shim:

.. code-block:: bash

   conda deactivate
   python --version

Install Gen3SchemaDev for use
-----------------------------

In your data dictionary project directory, create an isolated environment
and install Gen3SchemaDev:

.. code-block:: bash

   python -m venv .venv
   source .venv/bin/activate
   python -m pip install gen3schemadev
   gen3schemadev --version

For subsequent sessions, activate the environment again from the same directory:

.. code-block:: bash

   source .venv/bin/activate

