Upload the Synthetic FASTQ File
===============================

This example uploads ``sample-data/synthetic-demo.fastq`` to the local Gen3
commons. It uses the API credentials in the repository-root
``credentials.json`` and requests upload authorization for the existing
``training/demo`` project.

Keep the credentials file private. It is ignored by Git; do not remove it from
``.gitignore`` or print its contents.

Activate the shared Python environment and run the uploader from the repository
root:

.. code-block:: console

	source "$HOME/.gen3-local-tools/bin/activate"
	python src/upload_sample_file.py

The script asks Fence for a file GUID and a short-lived presigned S3 URL, then
transfers the FASTQ bytes to that URL. The URL and API token are not printed.
On success, the script prints the GUID, filename, byte size, and MD5 checksum.
The upload stores the bytes and creates the file's Indexd entry. It does not
submit a ``seqrun`` node to the project graph, which is why the file is not yet
listed in Gen3 Exploration.

If the authorization request fails, confirm that ``credentials.json`` is an
API credential for ``http://gen3.kind.test`` and that the user can upload to
``/programs/training/projects/demo``. If the storage PUT fails, check that the
local MinIO endpoint is reachable at ``http://minio.gen3.kind.test:9000`` and
that the infrastructure playbook has configured the local hostnames.

Once the file upload succeeds, use its actual GUID and metadata when preparing
the ``seqrun`` record, as described in :doc:`/08-gen3-sdk/02-sample-data`.

Register the file in project metadata
--------------------------------------

Before registering the file, submit the synthetic project metadata if you have
not already done so. The DNA parent ``SYN-DNA-001`` must exist in the
``training/demo`` project:

.. code-block:: console

	python sample-data/submit_sample_data.py

Then pass the GUID printed by the upload script to the registration script.
Use the full GUID, including any prefix such as ``PREFIX/``:

.. code-block:: console

	python src/register_sample_metadata.py 'PREFIX/your-guid-here'

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
