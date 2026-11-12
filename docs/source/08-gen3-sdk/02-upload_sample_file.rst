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
	python src/02-upload_sample_file.py

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
the ``seqrun`` record, as described in :doc:`/08-gen3-sdk/01-create_program`.

