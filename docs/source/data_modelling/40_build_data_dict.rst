
Build a Gen3 data dictionary
============================

The input file is stored at ``sample-data-dict/input.yaml``. To generate the data dictionary, run the following commands from the ``sample-data-dict`` directory:

.. code-block:: console

	mkdir -p output_schema

	gen3schemadev generate -i input.yaml -o output_schema



Validate the generated schemas before bundling them:

.. code-block:: console

	gen3schemadev validate -y output_schema

Fix validation errors in ``input.yaml``, remove or regenerate the generated output if necessary, and run the generation and validation commands again.
Now the individual node schemas can be combined into one JSON file. Create a directory for JSON output and write the bundle there:

.. code-block:: console

	mkdir -p output_json

	gen3schemadev bundle -i output_schema -f output_json/bundled_schema.json

The resulting ``output_json/bundled_schema.json`` contains the schemas needed to represent the complete data dictionary.
Then geenerate a visual representation from the bundled schema:

.. code-block:: console

	gen3schemadev visualise -i output_json/bundled_schema.json

You should be able to see the visual representation of the data dictionary in your browser. 

.. image:: images/graph_view.png
   :alt: Graph view of the data dictionary showing nodes and links
   :align: center
	:class: image-spaced

.. image:: images/properties.png
   :alt: Properties view of the data dictionary showing node properties and their attributes
   :align: center
	:class: image-spaced

.. image:: images/prop_details.png
   :alt: Details of the properties of the `Patient` node in the data dictionary.
   :align: center
	:class: image-spaced


Complete workflow
-----------------

From ``sample-data-dict``, the complete workflow is:

.. code-block:: console

	mkdir -p output_schema output_json

	gen3schemadev generate -i input.yaml -o output_schema

	gen3schemadev validate -y output_schema

	gen3schemadev bundle -i output_schema -f output_json/bundled_schema.json

	gen3schemadev visualise -i output_json/bundled_schema.json

After changing ``input.yaml``, repeat the workflow so that the generated schemas and bundled JSON reflect the updated data model.



