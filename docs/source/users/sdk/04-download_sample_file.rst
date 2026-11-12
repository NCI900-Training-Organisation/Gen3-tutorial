Download a File from Gen3
=========================

Which services handle the download?
------------------------------------

``Gen3Auth`` obtains an access token from **Fence**. ``Gen3Index`` reads the
file's name, size, and checksum from **Indexd**. ``Gen3File`` requests a download
URL from Fence, which uses the indexed location and **Arborist** permissions
to authorise access. The file bytes are downloaded from **MinIO** using that
presigned URL. The script checks the saved bytes against the Indexd metadata.

**Peregrine** is used to query graph metadata when discovering a file's GUID;
this example starts with a known GUID and does not query Peregrine.

This example downloads the synthetic FASTQ file previously uploaded to the
local Gen3 commons. It uses the API credentials in the repository-root
``credentials.json`` and Gen3's authenticated file-download API. The Gen3 SDK
obtains a short-lived access token and a presigned download URL internally;
the script does not display either value.

Activate the shared Python environment and run the downloader from the
repository root:

.. code-block:: console

	source "$HOME/.gen3-local-tools/bin/activate"
	python src/04-download_sample_file.py

By default, the script downloads GUID
``PREFIX/3ee620db-06c5-46c2-9bef-7e6729b8c8bd`` to ``downloads/``. It looks up
the filename, size, and MD5 in Indexd, then checks the downloaded file against
those values.

To download another file, provide its full GUID and optionally choose an
output directory:

.. code-block:: console

	python src/04-download_sample_file.py 'PREFIX/your-guid-here' --output-dir downloads

The script refuses to overwrite a local file by default. To intentionally
replace it, pass ``--overwrite``:

.. code-block:: console

	python src/04-download_sample_file.py --overwrite


