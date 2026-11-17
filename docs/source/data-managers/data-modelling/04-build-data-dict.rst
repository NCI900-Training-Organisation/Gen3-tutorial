
Build Data Dictionary
============================

Prepare your terminal
---------------------

Install Gen3SchemaDev using :doc:`03-setup-Gen3SchemaDev` first. From the
repository root, select your platform and activate the shared Python
environment. The selection stays synchronized with the other platform tabs
in this tutorial.

.. tab-set::
   :sync-group: operating-system

   .. tab-item:: macOS
      :sync: macos

      Use Terminal (Bash or Zsh).

      .. code-block:: bash

         source "$HOME/.gen3-local-tools/bin/activate"
         cd sample-data-dict

   .. tab-item:: Windows (WSL)
      :sync: windows

      Use a WSL Bash terminal, with Python, Gen3SchemaDev, and the repository
      inside WSL. Run the commands below in WSL rather than PowerShell.

      .. code-block:: bash

         source "$HOME/.gen3-local-tools/bin/activate"
         cd sample-data-dict

   .. tab-item:: Linux
      :sync: linux

      Use a Bash terminal.

      .. code-block:: bash

         source "$HOME/.gen3-local-tools/bin/activate"
         cd sample-data-dict

Generate, validate, and bundle
------------------------------

Select your platform for each command below. Run the commands in the same
terminal from the ``sample-data-dict`` directory. The input file is
``input.yaml``. Windows commands use WSL Bash.

.. tab-set::
   :sync-group: operating-system

   .. tab-item:: macOS
      :sync: macos

      .. code-block:: bash

          mkdir -p output-schema

          gen3schemadev generate -i input.yaml -o output-schema

   .. tab-item:: Windows (WSL)
      :sync: windows

      .. code-block:: bash

          mkdir -p output-schema

          gen3schemadev generate -i input.yaml -o output-schema

   .. tab-item:: Linux
      :sync: linux

      .. code-block:: bash

          mkdir -p output-schema

          gen3schemadev generate -i input.yaml -o output-schema


Validate the generated schemas before bundling them:

.. tab-set::
   :sync-group: operating-system

   .. tab-item:: macOS
      :sync: macos

      .. code-block:: bash

          gen3schemadev validate -y output-schema

   .. tab-item:: Windows (WSL)
      :sync: windows

      .. code-block:: bash

          gen3schemadev validate -y output-schema

   .. tab-item:: Linux
      :sync: linux

      .. code-block:: bash

          gen3schemadev validate -y output-schema


Fix validation errors in ``input.yaml``, remove or regenerate the generated output if necessary, and run the generation and validation commands again.
Now the individual node schemas can be combined into one JSON file. Create a directory for JSON output and write the bundle there:

.. tab-set::
   :sync-group: operating-system

   .. tab-item:: macOS
      :sync: macos

      .. code-block:: bash

          mkdir -p output-json

          gen3schemadev bundle -i output-schema -f output-json/bundled-schema.json

   .. tab-item:: Windows (WSL)
      :sync: windows

      .. code-block:: bash

          mkdir -p output-json

          gen3schemadev bundle -i output-schema -f output-json/bundled-schema.json

   .. tab-item:: Linux
      :sync: linux

      .. code-block:: bash

          mkdir -p output-json

          gen3schemadev bundle -i output-schema -f output-json/bundled-schema.json


The resulting ``output-json/bundled-schema.json`` contains the schemas needed to represent the complete data dictionary.
Then generate a visual representation from the bundled schema:

.. tab-set::
   :sync-group: operating-system

   .. tab-item:: macOS
      :sync: macos

      .. code-block:: bash

          gen3schemadev visualise -i output-json/bundled-schema.json

   .. tab-item:: Windows (WSL)
      :sync: windows

      .. code-block:: bash

          gen3schemadev visualise -i output-json/bundled-schema.json

   .. tab-item:: Linux
      :sync: linux

      .. code-block:: bash

          gen3schemadev visualise -i output-json/bundled-schema.json


You should be able to see the visual representation of the data dictionary in your browser. 

.. image:: /images/06-data-dictionary-graph-view.png
   :alt: Graph view of the data dictionary showing nodes and links
   :align: center
   :class: image-spaced

.. image:: /images/07-data-dictionary-properties.png
   :alt: Properties view of the data dictionary showing node properties and their attributes
   :align: center
   :class: image-spaced

.. image:: /images/08-data-dictionary-property-details.png
   :alt: Details of the properties of the `Patient` node in the data dictionary.
   :align: center
   :class: image-spaced


Complete workflow
-----------------

From ``sample-data-dict``, the complete workflow is:

.. tab-set::
   :sync-group: operating-system

   .. tab-item:: macOS
      :sync: macos

      .. code-block:: bash

          mkdir -p output-schema output-json

          gen3schemadev generate -i input.yaml -o output-schema

          gen3schemadev validate -y output-schema

          gen3schemadev bundle -i output-schema -f output-json/bundled-schema.json

          gen3schemadev visualise -i output-json/bundled-schema.json

   .. tab-item:: Windows (WSL)
      :sync: windows

      .. code-block:: bash

          mkdir -p output-schema output-json

          gen3schemadev generate -i input.yaml -o output-schema

          gen3schemadev validate -y output-schema

          gen3schemadev bundle -i output-schema -f output-json/bundled-schema.json

          gen3schemadev visualise -i output-json/bundled-schema.json

   .. tab-item:: Linux
      :sync: linux

      .. code-block:: bash

          mkdir -p output-schema output-json

          gen3schemadev generate -i input.yaml -o output-schema

          gen3schemadev validate -y output-schema

          gen3schemadev bundle -i output-schema -f output-json/bundled-schema.json

          gen3schemadev visualise -i output-json/bundled-schema.json


After changing ``input.yaml``, repeat the workflow so that the generated schemas and bundled JSON reflect the updated data model.
