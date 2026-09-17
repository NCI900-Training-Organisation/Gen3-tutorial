
Build a Gen3 data dictionary
============================

This page shows how to turn the example input file into a Gen3 data
dictionary. The input file is stored at
``sample-data-dict/input.yaml`` in the repository and describes the
following graph:


Install Gen3SchemaDev and confirm that the command is available:

.. code-block:: console

	$ gen3schemadev --version


Generate node schemas
---------------------

Create an output directory and generate one schema for each node:

.. code-block:: console

	$ mkdir -p output_schema
	$ gen3schemadev generate -i input.yaml -o output_schema

The generated files are written to ``output_schema``. Keep ``input.yaml`` as
the source input and treat the generated files as build artifacts.

Validate the generated dictionary
---------------------------------

Validate the generated schemas before bundling them:

.. code-block:: console

	$ gen3schemadev validate -y output_schema

Fix validation errors in ``input.yaml``, remove or regenerate the generated
output if necessary, and run the generation and validation commands again.

Create a bundled schema
-----------------------

The individual node schemas can be combined into one JSON file. Create a
directory for JSON output and write the bundle there:

.. code-block:: console

	$ mkdir -p output_json
	$ gen3schemadev bundle \
		 -i output_schema \
		 -f output_json/bundled_schema.json

The resulting ``output_json/bundled_schema.json`` contains the schemas needed
to represent the complete data dictionary.

Create a visualization
----------------------

Generate a visual representation from the bundled schema:

.. code-block:: console

	$ gen3schemadev visualise \
		 -i output_json/bundled_schema.json

The visualization command writes its output according to the installed
Gen3SchemaDev version. Check the command output for the generated file path.

Complete workflow
-----------------

From ``sample-data-dict``, the complete workflow is:

.. code-block:: console

	$ mkdir -p output_schema output_json
	$ gen3schemadev generate -i input.yaml -o output_schema
	$ gen3schemadev validate -y output_schema
	$ gen3schemadev bundle \
		 -i output_schema \
		 -f output_json/bundled_schema.json
	$ gen3schemadev visualise \
		 -i output_json/bundled_schema.json

After changing ``input.yaml``, repeat the workflow so that the generated
schemas and bundled JSON reflect the updated data model.



