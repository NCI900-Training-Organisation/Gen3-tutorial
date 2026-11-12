Register the file in project metadata
=====================================

Which services handle registration?
------------------------------------

The script reads the GUID's **Indexd** record and, when needed, finalises its
size, MD5 checksum, and storage location. It then uses ``Gen3Submission`` to
send the ``seqrun`` record to **Sheepdog**, which validates the data dictionary
and parent links before storing the record in **PostgreSQL**. **Fence** provides
the token; **Arborist** governs the relevant project permissions.

You can query the graph through **Peregrine** after submission. Exploration
uses **Guppy** over **Elasticsearch**, so it also needs an operator's **Tube**
refresh. Registration does not transfer the file bytes again.

Before registering the file, submit the synthetic project metadata if you have
not already done so. The DNA parent ``SYN-DNA-001`` must exist in the
``training/demo`` project:

Activate the shared environment and point the submission script at your API
credential file. Run these commands from the repository root:

.. code-block:: console

	source "$HOME/.gen3-local-tools/bin/activate"
	export GEN3_CREDENTIALS="$HOME/Downloads/gen3-credentials.json"
	python sample-data/submit_sample_data.py

The default credential path is ``~/Downloads/gen3-credentials.json`` when
``GEN3_CREDENTIALS`` is unset. If you saved the credential as the repository's
``credentials.json`` for the other SDK examples, set ``GEN3_CREDENTIALS`` to
that file's absolute path instead.

The script submits patients, blood and urine, then plasma and DNA, printing
the number of records submitted from each JSON file. The credential must allow
submission to ``training/demo``. This step submits graph metadata; it does not
upload bytes or create a ``seqrun``. Reusing the ``SYN-`` submitter IDs can update
existing records; change the IDs and their links together for another dataset.

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

After metadata submission succeeds, ask your operator to
:doc:`refresh search </operators/01-refresh-search>`, then reload Exploration.
Guppy serves the search index; Peregrine queries the graph directly.
