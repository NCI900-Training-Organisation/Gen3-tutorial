Tube
----

``Tube`` is a microservice that controls the ETL process of structured data.

.. note::

    - The data model defines the graph of nodes and relationships. 
    - ``Sheepdog`` validates structured submissions against that model and stores the submitted graph in PostgreSQL. 
    - ``Peregrine`` exposes the normalized graph through GraphQL.
    - ``Tube`` extracts selected graph data, transforms it according to the ETL mapping, and writes Elasticsearch documents. 
    - ``Guppy`` queries those documents, and the Exploration page uses ``Guppy`` to provide filters, cohort searches, tables, and charts.