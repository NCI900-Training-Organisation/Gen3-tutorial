Register the file in project metadata
=====================================

Before registering the file, submit the synthetic project metadata if you have
not already done so. The DNA parent ``SYN-DNA-001`` must exist in the
``training/demo`` project:

.. code-block:: console

	python sample-data/submit_sample_data.py

Then pass the GUID printed by the upload script to the registration script.
Use the full GUID, including any prefix such as ``PREFIX/``:

.. code-block:: console

	python src/03-register_sample_metadata.py 'PREFIX/your-guid-here'

The script submits a ``seqrun`` node with the file GUID, the FASTQ's actual
filename, size, MD5, and a link to ``SYN-DNA-001``. It does not upload the
bytes again. Its ``submitter_id`` is ``SYN-SEQRUN-001``; use a different ID if
you have already registered that sample or want to upload a second copy.

Refresh search
--------------

After the metadata submission succeeds, refresh Elasticsearch so the file is
included in Exploration:

.. code-block:: console

	ansible-playbook gen3-deployment/03-refresh-search.yaml

Wait for the playbook to complete successfully, then reload the portal's
Exploration page. If this is the first-ever ETL run and the bootstrap indices
are still in place, use the one-time force option documented in
:doc:`/06-local-gen3-deploy/01-local-deploy`.
