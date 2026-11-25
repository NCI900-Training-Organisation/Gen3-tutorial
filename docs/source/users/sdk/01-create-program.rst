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
The examples use the bundled dictionary in
``sample-data-dict/output-json/bundled-schema.json``.

Create the program and project first
------------------------------------

The bundled dictionary defines a ``program`` node and a ``project`` node.
A program is a top-level container for projects. In this tutorial, program
``training`` contains project ``demo``.

.. figure:: /images/06-data-dictionary-graph-view.png
   :alt: Data dictionary graph showing Program above Project, with patient and sample records linked below the project.
   :align: center
   :width: 100%



``program`` is marked ``submittable: false``. This means you cannot create a
program through the ordinary metadata submission process used for patient,
blood, or DNA records. An authorised administrator must create it through the
program-management API or an available portal administration feature.

.. note::

  In practice only an operator or administrator can create a program. In this case we are jus assuming 
  that the user has the necessary permissions to create a program for training purposes.
  
The program schema requires:

* ``name``: the program's name, such as ``training``.
* ``dbgap_accession_number``: its accession identifier. This tutorial uses
  ``LOCAL-SYNTHETIC`` as a training placeholder.

The script ``src/01-create_program.py --create-program`` creates the program
through the SDK's administrative API. Once the program exists, you can create
its project and submit metadata.

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
``file_state``, ``object_id`` and ``state``. 

Do not create a sample ``seqrun``
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
in :doc:`03-register-sample-metadata`. Reusing the same ``submitter_id`` values can update
or collide with earlier records, so make identifiers unique when adapting
these examples.

How the data model guides submissions
-------------------------------------

The tutorial's data model starts in ``sample-data-dict/input.yaml``. The
generated YAML files in ``sample-data-dict/output-schema/`` spell out the
rules for each record type. Those rules are bundled into
``sample-data-dict/output-json/bundled-schema.json``, which Gen3 uses to
check submissions.

For example, ``blood.yaml`` says a blood record must link to a patient using
the ``patients`` field. Your ``blood.json`` supplies the actual patient ID,
``SYN-PAT-001``. Read the YAML to find what to put in your submission JSON.
Look under ``links:`` to see what each record can connect to.

What ``patient.json`` does
~~~~~~~~~~~~~~~~~~~~~~~~~~

When the tutorial submits ``patient.json``, it asks Gen3 to create two sample
patient records in the existing ``demo`` project. Their IDs are ``SYN-PAT-001``
and ``SYN-PAT-002``.

The patient rule appears in `patient.yaml <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/sample-data-dict/output-schema/patient.yaml#L25>`_.

.. literalinclude:: ../../../../sample-data-dict/output-schema/patient.yaml
   :language: yaml
   :start-at: links:
   :end-before: properties:

``name: projects`` gives the field to use in the JSON. ``target_type: project``
says it must point to a project, and ``required: true`` means the patient must
include that link. This example uses the project code ``demo``.


Read the first record as **“Create a patient called SYN-PAT-001 in the demo
project.”** Each field contributes one piece of information.

.. list-table::
   :header-rows: 1

   * - Field
     - What it means
   * - ``"type": "patient"``
     - This is a patient record. Gen3 uses the patient rules from the data model
       to check it.
   * - ``"submitter_id": "SYN-PAT-001"``
     - This is the ID we give the record. Later, a blood sample can use it to
       point to this patient.
   * - ``"patient_id": "SYN-PAT-001"``
     - This is an extra patient ID field. The example gives it the same value
       as ``submitter_id``.
   * - ``"projects": [{"code": "demo"}]``
     - The patient model requires a ``projects`` link to one existing project.
       The code ``demo`` tells Gen3 which project this patient belongs to.

The second record follows the same pattern with ``SYN-PAT-002``. When the
tutorial submits ``blood.json`` later, the first blood sample uses
``SYN-PAT-001`` to link to the first patient, and the second uses
``SYN-PAT-002`` to link to the second patient.

Submit the blood records
~~~~~~~~~~~~~~~~~~~~~~~~

The blood rule appears in `blood.yaml <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/sample-data-dict/output-schema/blood.yaml#L25>`_.

.. literalinclude:: ../../../../sample-data-dict/output-schema/blood.yaml
   :language: yaml
   :start-at: links:
   :end-before: properties:

``name: patients`` is the field in ``blood.json``. ``target_type: patient``
says it points to a patient, and ``required: true`` means every blood sample
needs that link. The sample supplies the specific patient, ``SYN-PAT-001``.

The first record in ``sample-data/blood.json`` gives Gen3 these values.

.. list-table::
   :header-rows: 1

   * - Field
     - What it means
   * - ``"type": "blood"``
     - Gen3 checks this record against the blood model.
   * - ``"submitter_id": "SYN-BLD-001"``
     - This gives the record its ID within the project.
   * - ``"blood_id": "SYN-BLD-001"``
     - The sample's blood ID.
   * - ``"blood_type": "whole blood"``
     - This describes the sample as whole blood.
   * - ``"patients": [{"submitter_id": "SYN-PAT-001"}]``
     - The blood model requires each blood sample to point to one patient. This link records whose blood was collected, so the patient must be submitted first.

The second record, ``SYN-BLD-002``, points to ``SYN-PAT-002``.

Submit the urine record
~~~~~~~~~~~~~~~~~~~~~~~

The urine rule appears in `urine.yaml <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/sample-data-dict/output-schema/urine.yaml#L25>`_.

.. literalinclude:: ../../../../sample-data-dict/output-schema/urine.yaml
   :language: yaml
   :start-at: links:
   :end-before: properties:

``name: patients`` and ``target_type: patient`` allow the same kind of link
as blood uses. Here, ``required: false`` makes it optional. The sample
includes it to record that ``SYN-URN-001`` came from ``SYN-PAT-001``.

The first record in ``sample-data/urine.json`` gives Gen3 these values.

.. list-table::
   :header-rows: 1

   * - Field
     - What it means
   * - ``"type": "urine"``
     - Gen3 checks this record against the urine model.
   * - ``"submitter_id": "SYN-URN-001"``
     - This gives the record its ID within the project.
   * - ``"urine_id": "SYN-URN-001"``
     - The sample's urine ID.
   * - ``"patients": [{"submitter_id": "SYN-PAT-001"}]``
     - The urine model allows this link to one patient and makes it optional. This example includes it so Gen3 knows whose urine was collected.

This file contains one record, linked to the first patient.

Submit the plasma records
~~~~~~~~~~~~~~~~~~~~~~~~~

The plasma rule appears in `plasma.yaml <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/sample-data-dict/output-schema/plasma.yaml#L25>`_.

.. literalinclude:: ../../../../sample-data-dict/output-schema/plasma.yaml
   :language: yaml
   :start-at: links:
   :end-before: properties:

``name: bloods`` and ``target_type: blood`` tell you where to put the link
and what it must point to. ``required: true`` means the link is required,
and ``one_to_one`` pairs the plasma record with one blood sample. The
example names ``SYN-BLD-001``.

The first record in ``sample-data/plasma.json`` gives Gen3 these values.

.. list-table::
   :header-rows: 1

   * - Field
     - What it means
   * - ``"type": "plasma"``
     - Gen3 checks this record against the plasma model.
   * - ``"submitter_id": "SYN-PLA-001"``
     - This gives the record its ID within the project.
   * - ``"plasma_id": "SYN-PLA-001"``
     - The sample's plasma ID.
   * - ``"bloods": [{"submitter_id": "SYN-BLD-001"}]``
     - The plasma model requires a link to one blood record. This link records which blood sample the plasma came from. Submit the blood first. Gen3 can then reach the patient through that blood record.

The second record, ``SYN-PLA-002``, points to ``SYN-BLD-002``.

Submit the DNA records
~~~~~~~~~~~~~~~~~~~~~~

The DNA rule appears in `dna.yaml <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/sample-data-dict/output-schema/dna.yaml#L25>`_.

.. literalinclude:: ../../../../sample-data-dict/output-schema/dna.yaml
   :language: yaml
   :start-at: links:
   :end-before: properties:

``name: bloods`` and ``target_type: blood`` make this a link to a blood
record. ``required: true`` requires the link, and ``one_to_one`` pairs the
DNA record with one blood sample. The example names ``SYN-BLD-001``.

The first record in ``sample-data/dna.json`` gives Gen3 these values.

.. list-table::
   :header-rows: 1

   * - Field
     - What it means
   * - ``"type": "dna"``
     - Gen3 checks this record against the DNA model.
   * - ``"submitter_id": "SYN-DNA-001"``
     - This gives the record its ID within the project.
   * - ``"dna_id": "SYN-DNA-001"``
     - The DNA record's DNA ID.
   * - ``"dna_specimen_id": "SYN-DNA-001"``
     - The specimen ID. This example uses the same value for both DNA fields.
   * - ``"bloods": [{"submitter_id": "SYN-BLD-001"}]``
     - The DNA model requires a link to one blood record. This link records which blood sample the DNA came from. The DNA and plasma records both point directly to the blood sample.

The second record, ``SYN-DNA-002``, points to ``SYN-BLD-002``.

Register the sequencing file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After uploading ``synthetic-demo.fastq``, the tutorial runs
``src/03-register_sample_metadata.py`` with the file ID returned by the upload.
The script submits the following record details to ``training/demo``.

The sequencing-run rule appears in `seqrun.yaml <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/sample-data-dict/output-schema/seqrun.yaml#L25>`_.

.. literalinclude:: ../../../../sample-data-dict/output-schema/seqrun.yaml
   :language: yaml
   :start-at: links:
   :end-before: properties:

In the first entry under ``subgroup``, ``name: dnas`` and ``target_type: dna``
define a link to DNA. That entry says ``required: true``. The sample run
links to ``SYN-DNA-001``. The second entry defines an optional link to a
metadata collection, which this example leaves empty.


.. list-table::
   :header-rows: 1

   * - Field
     - What it means
   * - ``"type": "seqrun"``
     - Gen3 checks this record against the sequencing-run model in ``seqrun.yaml``.
   * - ``"submitter_id": "SYN-SEQRUN-001"``
     - This is the ID for the sequencing-run record.
   * - ``"seqrun_id": "SYN-SEQRUN-001"``
     - This is the sequencing-run ID field. The script uses the same value here.
   * - ``object_id``
     - This is the file ID returned by the upload. It connects this metadata to the uploaded file.
   * - ``"file_name": "synthetic-demo.fastq"``
     - This is the name of the file the record describes.
   * - ``file_size, md5sum``
     - The script reads the file size in bytes and computes a checksum, a value used to check the file's contents.
   * - ``"state": "uploaded"``
     - The script records that the file has already been uploaded.
   * - ``"dnas": [{"submitter_id": "SYN-DNA-001"}]``
     - The sequencing-run model requires a ``dnas`` link. This example names the DNA used for the run, so the DNA record must exist first.

This gives Gen3 a path from ``SYN-SEQRUN-001`` to ``SYN-DNA-001``, then to
``SYN-BLD-001``, and finally to ``SYN-PAT-001``.
