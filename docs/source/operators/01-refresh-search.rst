Refresh Search After Metadata Submission
========================================

After users submit metadata through Sheepdog, the graph records are stored in
PostgreSQL. Exploration uses a transformed representation in Elasticsearch,
queried through Guppy. Refresh that representation after new submissions.

Run from the repository root with the deployment environment configured:

.. code-block:: console

   ansible-playbook gen3-deployment/03-refresh-search.yaml

The playbook runs the Tube ETL workflow. Wait for it to finish successfully,
then ask users to reload Exploration. For the first ETL run with bootstrap
indices, follow the one-time force option in
:doc:`/operators/local-deployment/01-local-deploy`.

A file can be downloadable by GUID before it appears in Exploration: file
access uses Fence and Indexd, while search depends on the graph submission
and ETL refresh.
