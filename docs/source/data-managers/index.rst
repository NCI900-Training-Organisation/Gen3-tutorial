Data Managers
=============

Follow this stream to understand data modelling, design nodes and
relationships, and build the dictionary that defines valid submissions.
Start with Data Modelling 101, then develop and validate the model using
Gen3SchemaDev.

.. toctree::
   :maxdepth: 2

   data-modelling/01-data-modelling-101
   data-modelling/02-data-dictionary
   data-modelling/03-setup-Gen3SchemaDev
   data-modelling/04-build-data-dict

The model build produces ``sample-data-dict/output-json/bundled-schema.json``.
Coordinate with an :doc:`operator </operators/index>` to deploy the dictionary
and update search configuration. Users then follow the
:doc:`metadata submission guide </users/sdk/03-register_sample_metadata>`
to submit records that conform to it.
