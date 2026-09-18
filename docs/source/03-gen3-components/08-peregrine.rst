Peregrine
---------

``Peregrine`` is the metadata-seeking service that responds to GraphQL search
queries. It translates them to queries over the graph-like PostgreSQL database
for structured data.

.. note::

    * ``Peregrine`` queries the complete PostgreSQL graph and is useful when a query depends on the original relationships.
    * ``Guppy`` queries the Elasticsearch representation and is useful for fast, repeated Explorer searches.