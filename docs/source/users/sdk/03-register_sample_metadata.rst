Register the File in Project Metadata
=====================================

This guide provides the commands to submit the synthetic parent records and
register an uploaded FASTQ file as a ``seqrun`` in ``training/demo``. Run the
commands from the repository root in the same terminal session. If a previous
step is already complete, continue from the next step.

Prepare the environment and credentials
---------------------------------------

Install the SDK as described in :doc:`/users/03-install-sdk`, then activate the
shared environment:

.. code-block:: console

   cd /path/to/Gen3-tutorial
   source "$HOME/.gen3-local-tools/bin/activate"
   export GEN3_ENDPOINT="http://gen3.kind.test"
   export GEN3_CREDENTIALS="$PWD/credentials.json"

Replace ``/path/to/Gen3-tutorial`` with your repository location. The scripts
in ``src/`` read ``credentials.json`` from the repository root. Here we assume that ``credentials.json`` 
is available in the repository root. Keep the credentials file private.

**Fence** exchanges it for an access token; **Arborist** governs the relevant
project permissions.

Create the program and project if needed
----------------------------------------

Your account must have permission to create programs and projects. If neither
``training`` nor ``demo`` exists, run:

.. code-block:: console

   python src/01-create_program.py --create-program

If ``training`` already exists but ``demo`` does not, run this command instead:

.. code-block:: console

   python src/01-create_program.py

Skip both commands if ``training/demo`` already exists. These are creation
commands, so do not run both in sequence. See :doc:`01-create_program` for the
required fields and the meaning of ``submittable: false``.

Submit the patient and sample records
-------------------------------------

The DNA parent ``SYN-DNA-001`` must exist before the file record can link to it.
Submit the JSON records in dependency order: patient, blood, urine, plasma,
and DNA. This command uses **Sheepdog** to validate the records against the
data dictionary and store them in **PostgreSQL**:

.. code-block:: console

   python - <<'PY'
   import json
   import os
   from pathlib import Path

   from gen3.auth import Gen3Auth
   from gen3.submission import Gen3Submission

   credentials = Path(os.environ["GEN3_CREDENTIALS"]).expanduser()
   if not credentials.is_file():
       raise SystemExit(f"Credentials file not found: {credentials}")

   auth = Gen3Auth(
       endpoint=os.environ["GEN3_ENDPOINT"],
       refresh_file=str(credentials),
   )
   submission = Gen3Submission(auth)
   for name in ("patient", "blood", "urine", "plasma", "dna"):
       path = Path("sample-data") / f"{name}.json"
       records = json.loads(path.read_text(encoding="utf-8"))
       submission.submit_record("training", "demo", records)
       print(f"Submitted {len(records)} records from {path.name}.")
   PY

* **Metadata submission:** This command submits patient, blood, urine, plasma,
  and DNA records. Uploading the FASTQ bytes and creating its ``seqrun``
  metadata record are separate steps, shown below.

* **Reusing IDs:** The sample submitter IDs identify records within the project.
  Running the command again with IDs such as ``SYN-PAT-001`` may update
  existing records instead of creating a separate dataset.

* **Creating a separate dataset:** Change the IDs and their references together
  in the sample JSON files. For example, if you rename patient ``SYN-PAT-001``
  to ``SYN-PAT-002``, update the patient references in its blood and urine
  records to ``SYN-PAT-002`` too. Otherwise, the new samples could remain linked
  to the old patient. Apply the same rule to the links between blood, plasma,
  DNA, and file records.

Upload the FASTQ file if needed
-------------------------------

If you have not uploaded the file yet, run:

.. code-block:: console

   python src/02-upload_sample_file.py

**Fence** authorises the upload and returns a GUID and presigned URL. The
script transfers bytes to **MinIO**, and **Indexd** tracks the object. Retain
the GUID printed by the script. If the upload is already complete, use its
existing GUID instead of uploading another copy.

Register the uploaded file
--------------------------

Replace the example value with the full GUID printed by the uploader,
including any prefix such as ``PREFIX/``:

.. code-block:: console

   export GEN3_FILE_GUID='PREFIX/your-guid-here'
   python src/03-register_sample_metadata.py "$GEN3_FILE_GUID"

The registration script reads the **Indexd** record and, when needed, finalises
its size, MD5 checksum, and storage location. It then submits a ``seqrun`` to
**Sheepdog**, using the FASTQ's actual filename, size, MD5, and a link to
``SYN-DNA-001``. It does not transfer the bytes again.

The file record's ``submitter_id`` is ``SYN-SEQRUN-001``. To register a different
sample, edit ``SEQ_RUN_SUBMITTER_ID`` and, if applicable,
``DNA_SUBMITTER_ID`` in ``src/03-register_sample_metadata.py`` before running
it. Keep the source file and upload bucket settings consistent with the file
that was actually uploaded.

Refresh search
--------------

**Peregrine** can query the graph after metadata submission. Exploration uses
**Guppy** over **Elasticsearch** and also requires a **Tube** refresh. An
operator with access to the deployment runs:

.. code-block:: console

   ansible-playbook gen3-deployment/03-refresh-search.yaml


.. note::

	In practice, only an operator or administrator can refresh search. In this case we are just assuming that the user 
	has the necessary permissions to refresh search for training purposes.

For the first ETL run, when only the bootstrap indices exist, use this command
instead:

.. code-block:: console

   ansible-playbook gen3-deployment/03-refresh-search.yaml -e etl_force=true

Wait for the playbook to finish successfully, then reload Exploration in the
browser. See :doc:`/operators/01-refresh-search` for the operator workflow.


