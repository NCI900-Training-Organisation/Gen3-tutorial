Data Managers
=============

Follow this stream to understand data modelling, design nodes and
relationships, and build the dictionary that defines valid submissions.
Start with Data Modelling 101, then develop and validate the model using
Gen3SchemaDev.

.. toctree::
   :maxdepth: 2

   data-modelling/index
   etl/index

The model build produces ``sample-data-dict/output-json/bundled-schema.json``.
Coordinate with an :doc:`operator </operators/index>` to deploy the dictionary
and update search configuration. Users then follow the
:doc:`metadata submission guide </users/sdk/03-register-sample-metadata>`
to submit records that conform to it.
