Design an ETL mapping from your data model
==========================================

Start with your generated node schemas and bundled data dictionary.
Gen3 uses the dictionary to validate submissions. The ETL mapping tells
Tube which submitted records to turn into search entries and what to
include in each entry.

1. Decide what one search result represents
-------------------------------------------

Write down what people should be able to find in the Explorer. For each
kind of result, decide what one row represents, which values users need
to see, and which values they need to filter by. Use this list to decide
what to index.

2. Choose how Tube should build each result
-------------------------------------------

Use an ``aggregator`` when each result starts from one kind of record in
your data model. Set ``root`` to that node type. Use a ``collector`` when
you want to gather records from a category, such as ``data_file``. Check
which nodes belong to that category and which ones your mapping should
target. A category-based collector can use ``root: None``.

Give the mapping a ``name`` for its Elasticsearch index and a
``doc_type`` label for the kind of result it produces.

3. Find where each value comes from
-----------------------------------

For each value you want to index, find the node and field in the
generated schemas. Check any shared definitions the node refers to.
Use ``props`` to copy fields directly from the records the mapping starts
with. If you want to rename a field, use ``src`` for the source field and
``name`` for the output field.

4. Trace the path to any related records
----------------------------------------

Start at the record that will become the search result. Read the
``links`` definitions in your schemas and write down each step. Use
``name`` when following a link in the direction it was submitted and
``backref`` when following it in reverse. Join successive link names
with dots. Check whether each step can lead to zero, one, or several
records. That affects how you can use the values you find.

5. Choose what to do with the related values
--------------------------------------------

* Use ``flatten_props`` to copy fields from a linked lower-level record
  into the result. If several records can match, decide which one should
  provide the values.
* Use ``aggregated_props`` to summarize related records. For a count,
  specify the ``path`` to follow, ``fn: count``, and a ``name`` for the
  output field.
* Use ``injecting_props`` to add fields from related parent records to
  entries built by a collector.
* Use ``joining_props`` to bring in fields from another ETL index.
  Identify the shared field to match on and specify it with ``join_on``.

6. Connect the indexed results to the Explorer
----------------------------------------------

Deploy the mapping and configure Guppy to expose each index the portal
needs. In the Explorer configuration, set each tab's ``guppyConfig.dataType``
to match the label Guppy exposes for that index. Choose the indexed
fields to show as columns or offer as filters.

7. Check the results with a small submission
--------------------------------------------

Choose a few test records whose expected results you can work out by
hand. Include missing optional links and multiple linked records where
the schema allows them. Write down the expected rows, field values, and
counts before running ETL.

Submit the test records, run the search refresh, and compare the indexed
results with your expectations. Then check the Explorer tabs, columns,
and filters. If a value is missing, first check the submitted data and
the mapping's field names and link directions. If the value is present
in the index, check the Guppy and Explorer settings.
