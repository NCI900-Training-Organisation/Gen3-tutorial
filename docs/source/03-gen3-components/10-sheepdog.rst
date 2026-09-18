Sheepdog
--------

The ``Sheepdog`` service manages user submissions of metadata into the graph
database. The submissions are quality controlled against the data dictionary to
ensure all required fields are present and have appropriate data values.
``Sheepdog`` also supports bulk export of the metadata into TSV or JSON formats.

.. note::
    
    * ``Sheepdog`` validates structured submissions against that model and stores the submitted graph in PostgreSQL. 
    
    * ``Peregrine`` exposes the normalized graph through GraphQL.