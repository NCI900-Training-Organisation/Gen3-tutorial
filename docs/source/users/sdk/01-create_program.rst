Create the Program and Project
==============================

Which services handle project and metadata submission?
------------------------------------------------------

``Gen3Submission`` calls **Sheepdog** for project creation and structured
metadata submission. Sheepdog validates submitted records against the deployed
data dictionary and persists them in **PostgreSQL**. **Fence** supplies the
access token, and project permissions are governed by **Arborist** policies.
Creating programs and projects requires the appropriate administrative access;
ask your operator to create them if your account cannot do so.

This guide explains the records in ``sample-data/`` and the fields and links
your own data must contain before submitting it to the local Gen3 commons.
The examples are synthetic and use the bundled dictionary in
``sample-data-dict/output-json/bundled-schema.json``. Never use real patient
information for this training exercise.

Create the program and project first
------------------------------------

The bundled dictionary defines a ``program`` node and a ``project`` node.
``program`` is marked ``submittable: false``, so create the program through the
portal or the approved administrative workflow, not with the sample records.
The program schema requires ``name`` and ``dbgap_accession_number``.

Run the project creation script from the repository root, using your API
credentials in ``credentials.json``:

.. code-block:: console

	python src/01-create_program.py

If the ``training`` program does not exist yet, create it together with the
project:

.. code-block:: console

	python src/01-create_program.py --create-program

The sample submission script targets program ``training`` and project code
``demo``. Create those first, or update the values in
``sample-data/submit_sample_data.py`` to match a project that already exists
and that your API user can access. The project schema requires:

* ``code``: project identifier; the sample uses ``demo``.
* ``name``: display name for the project.
* ``programs``: link to its parent program, for example
	``{"name": "training"}`` in the project's creation form/API. The SDK's
	project-creation method also takes the program name separately as its first
	argument.
* ``dbgap_accession_number``: the accession assigned to the project. Use the
	value appropriate to your environment; do not copy a made-up accession into
	a real commons.

Submit each record's required fields
------------------------------------

Every submittable node in this dictionary requires ``type`` and
``submitter_id``. The ``type`` must exactly match the node name. A
``submitter_id`` is the stable, project-specific identifier for that record;
keep it unique within its node and project. The samples use the ``SYN-`` prefix
so their identifiers are visibly synthetic.

The bundled sample files contain these nodes and required relationships:

.. list-table:: Sample records and required fields
   :header-rows: 1
   :widths: 16 24 30 30

   * - Node
     - Sample file
     - Required fields
     - Relationship to include
   * - ``patient``
     - ``sample-data/patient.json``
     - ``type``, ``submitter_id``
     - ``projects`` must identify the existing project by ``code`` or ID.
   * - ``blood``
     - ``sample-data/blood.json``
     - ``type``, ``submitter_id``
     - ``patients`` must identify an existing patient by ``submitter_id`` or ID.
   * - ``urine``
     - ``sample-data/urine.json``
     - ``type``, ``submitter_id``
     - ``patients`` is optional, but the example links the urine to its patient.
   * - ``plasma``
     - ``sample-data/plasma.json``
     - ``type``, ``submitter_id``
     - ``bloods`` must identify an existing blood record.
   * - ``dna``
     - ``sample-data/dna.json``
     - ``type``, ``submitter_id``
     - ``bloods`` must identify an existing blood record.

The node schemas allow only declared properties. Before adding fields, check
the node's schema under ``sample-data-dict/output-schema/``. For example,
``patient`` permits the optional ``patient_id`` property, ``blood`` permits
``blood_id``, ``patient_id`` and ``blood_type``, and ``dna`` permits
``dna_id``, ``blood_id`` and ``dna_specimen_id``. A property listed in
``sample-data-dict/input.yaml`` is not automatically a valid field name for a
relationship: use the schema's actual relationship property such as
``patients`` or ``bloods``.

Represent links as references to existing records. This patient example links
to the existing project ``demo``:

.. code-block:: json

	 {
		 "type": "patient",
		 "submitter_id": "SYN-PAT-001",
		 "patient_id": "SYN-PAT-001",
		 "projects": [{"code": "demo"}]
	 }

A blood record links back to a patient using the schema's ``patients`` link:

.. code-block:: json

	 {
		 "type": "blood",
		 "submitter_id": "SYN-BLD-001",
		 "blood_id": "SYN-BLD-001",
		 "blood_type": "whole blood",
		 "patients": [{"submitter_id": "SYN-PAT-001"}]
	 }

The example's matching ``SYN-PAT-001`` and ``SYN-BLD-001`` values are present
in the patient and blood files respectively. Do not submit a child record
before the record it links to exists.

Sequencing files and file metadata
----------------------------------

The ``seqrun`` node is categorized as ``data_file`` and links to a DNA record
through ``dnas``. It inherits file properties from the dictionary's
``data_file_properties``, including ``file_name``, ``file_size``, ``md5sum``,
``file_state``, ``object_id`` and ``state``. Do not create a sample ``seqrun``
with guessed file details. First upload a real synthetic test file through
Gen3, then use the returned GUID as ``object_id`` and the actual filename,
size, and checksum. Link it to an existing DNA record with ``dnas``. The
``data_category``, ``data_format`` and ``data_type`` fields must use the exact
enum values declared in ``sample-data-dict/output-schema/seqrun.yaml``.

Submit in relationship order
----------------------------

Submit parent records before children so every reference resolves:

#. Create the ``training`` program and ``demo`` project in the portal if they
	 do not already exist.
#. Submit patients.
#. Submit blood and urine records.
#. Submit plasma and DNA records.
#. Upload any test file, then submit its ``seqrun`` metadata with the returned
	 GUID and a link to its DNA record.

The helper script submits the provided JSON files in that order through the
Gen3 Python SDK. See :doc:`/users/03-install-sdk` for SDK setup and
:doc:`/users/api-credentials/01-gen-token` for API credentials and authentication.
To submit the synthetic sample set, follow the prerequisite submission steps
in :doc:`03-register_sample_metadata`. Reusing the same ``submitter_id`` values can update
or collide with earlier records, so make identifiers unique when adapting
these examples.
