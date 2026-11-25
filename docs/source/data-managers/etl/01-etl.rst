How ETL uses submitted data
===========================

Read the tutorial's ETL mapping
-------------------------------

Here is the full mapping that Tube uses for this tutorial. A single
Tube run uses both entries. ``training_patient`` builds the patient index,
and ``training_file`` builds the file index in Elasticsearch.

.. literalinclude:: ../../../../gen3-deployment/config/gen3-values.yaml
   :language: yaml
   :start-at: etlMapping:
   :end-before: image:
   :dedent: 2

ETL basics
----------

ETL stands for **Extract, Transform, Load**. The Tube service does this
work when you run the search refresh.

1. **Extract.** Tube reads the submitted records and their saved links from
   PostgreSQL.
2. **Transform.** Tube follows the mapping to copy fields, follow links,
   and calculate counts.
3. **Load.** Tube saves the results as search entries in Elasticsearch.

In :ref:`sdk-data-model-submissions`, the schema defines which links are
allowed and the submission names the records to connect. ETL uses those
saved connections to prepare data for the Explorer.

How to read each mapping entry
------------------------------

* **name and doc_type.** ``name`` names the Elasticsearch index.
  ``doc_type`` names the kind of search document produced by the mapping.
  Here, ``training_patient`` produces ``patient`` documents and
  ``training_file`` produces ``file`` documents.

  .. note::

     You choose the ``doc_type`` label when you write the ETL mapping.
     Your tutorial uses ``patient`` for patient summaries and ``file`` for
     search entries built from sequencing-run records.

     .. list-table::
        :header-rows: 1

        * - Where the label is used
          - Patients
          - Files
        * - ETL names the kind of search result
          - ``doc_type: patient``
          - ``doc_type: file``
        * - Guppy maps the label to an Elasticsearch index
          - ``type: patient`` uses ``training_patient``
          - ``type: file`` uses ``training_file``
        * - The Explorer tab asks Guppy for that kind of result
          - ``"dataType": "patient"``
          - ``"dataType": "file"``

     If the tab asks for a different label, Guppy won't find the intended
     index under that label.
     See `the Guppy index configuration <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/gen3-deployment/config/gen3-values.yaml#L369-L372>`_,
     `the Patients tab setting <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/gen3-deployment/config/gen3-values.yaml#L648>`_,
     and `the Files tab setting <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/gen3-deployment/config/gen3-values.yaml#L699>`_.

* **type and root.** The patient mapping is an ``aggregator``.
  ``root: patient`` tells Tube to start from a patient and build one
  summary for each patient. The file mapping is a ``collector``, with
  ``root: None``. It uses ``category: data_file`` and
  ``target_nodes`` naming ``seqrun`` to specify what to collect.

  .. note::

     The Files tab needs an entry for each sequencing file. The
     ``collector`` builds those entries from file records. In this mapping,
     ``root: None`` means there is no separate root record such as
     ``patient``. The collector uses ``category: data_file`` and
     ``target_nodes`` to identify what to collect. The target here is
     ``seqrun``.

     For example, Tube starts with ``SYN-SEQRUN-001``, the record that
     describes ``synthetic-demo.fastq``. It then follows
     ``dnas.bloods.patients`` to find the patient associated with that file.

* **props.** These are the fields Tube copies directly into a search
  entry. Think of a simple field as a possible table column. The portal
  can choose to show it or use it as a filter. A field can also be renamed.
  Your patient mapping uses ``src: id`` to save Gen3's internal patient ID
  under the name ``_patient_id``.

  .. note::

     ``id`` is a built-in Gen3 field listed under ``systemProperties`` in
     the patient schema. Gen3 assigns it when it creates the record.
     Your submission supplies ``submitter_id``, such as ``SYN-PAT-001``.

     In ``src: id``, ``src`` tells Tube which source field to read.
     Together with ``name: _patient_id``, it tells Tube to copy Gen3's
     internal ID into the search entry as ``_patient_id``.
     See `the patient schema <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/sample-data-dict/output-schema/patient.yaml#L12-L17>`_.

* **path and fn.** ``path`` tells Tube which link to follow from the
  starting record. A dot separates successive links. ``fn`` is the
  operation to perform, such as ``count``.

  .. note::

     The schema gives each connection a name in both directions. In
     ``blood.yaml`` and ``urine.yaml``, ``name: patients`` is the field the
     submitted sample uses to point to a patient. The ``backref`` names the
     link in the reverse direction, from the patient back to the samples.

     * ``path: bloods`` comes from ``backref: bloods`` in
       `blood.yaml <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/sample-data-dict/output-schema/blood.yaml#L25-L31>`_.
       From ``SYN-PAT-001``, it leads to ``SYN-BLD-001``.
     * ``path: urines`` comes from ``backref: urines`` in
       `urine.yaml <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/sample-data-dict/output-schema/urine.yaml#L25-L31>`_.
       From ``SYN-PAT-001``, it leads to ``SYN-URN-001``.

     The mapping uses these reverse names because ``root: patient`` tells
     Tube to start at the patient.

* **flatten_props.** This copies fields from a linked lower-level record.
  Your mapping has no ``flatten_props``. Gen3 shows both a one-to-one
  example and an example with several linked events where sorting by date
  lets Tube take fields from the most recent event.

* **aggregated_props.** This summarizes linked records. Your patient
  mapping uses ``path: bloods`` and ``fn: count`` to count the blood
  records for each patient. For ``SYN-PAT-001``, Tube saves
  ``_blood_count: 1``. The other rules count urine samples, DNA records,
  and sequencing runs.

* **joining_props.** This brings fields from another index into the
  search entry Tube is building. ``join_on`` specifies the field the two
  indices have in common. For example, a patient mapping could match
  patient and file entries on ``_patient_id`` to include file IDs in a
  patient summary. Your mapping has no ``joining_props``.

* **injecting_props.** This adds information from related records to the
  collector's search entries. Your file mapping follows
  ``dnas.bloods.patients`` from the sequencing run to the patient and adds
  the linked patient's Gen3 ID as ``_patient_id``, along with
  ``project_id``. This gives the search entry for
  ``synthetic-demo.fastq`` its patient association.

.. note::

   A dot separates successive links. Read ``dnas.bloods.patients`` from
   left to right. Each step starts at the record found in the previous step.

   1. ``dnas`` goes from sequencing run ``SYN-SEQRUN-001`` to DNA record
      ``SYN-DNA-001``.
   2. ``bloods`` goes from that DNA record to blood sample ``SYN-BLD-001``.
   3. ``patients`` goes from that blood sample to patient ``SYN-PAT-001``.

   Tube uses the patient at the end of this path to add patient information
   to the search entry for ``synthetic-demo.fastq``.

See the `Gen3 Forum Tube mapping examples <https://gen3.org/community/events/Gen3%20Forum%20September%202025%20-%20ETL.pdf>`_.

How the mapping relates to the portal
-------------------------------------

The ETL mapping selects the records and fields to put into Elasticsearch
and describes how to transform them. Guppy makes those indexed fields
available to the Explorer. The portal's ``explorerConfig`` chooses the tabs,
table columns, and filters that users see. For example, your Patients tab
shows the blood count because Tube indexes ``_blood_count`` and the portal
lists it as a column. Adding another ETL mapping by itself won't add a tab.
See the `Gen3 search documentation <https://docs.gen3.org/gen3-resources/operator-guide/customize-search/>`_.

Why the submission says patients and ETL says bloods
----------------------------------------------------

The ETL setting ``path: bloods`` comes from ``backref: bloods`` in the
blood schema. The schema gives the same connection two names, depending on
where you start.
See `the blood schema's link rule <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/sample-data-dict/output-schema/blood.yaml#L25-L31>`_.

.. literalinclude:: ../../../../sample-data-dict/output-schema/blood.yaml
   :language: yaml
   :start-at: links:
   :end-before: properties:

* **Start at the blood sample.** The schema's ``name: patients`` tells you
  which field to use in ``blood.json`` to link ``SYN-BLD-001`` to
  ``SYN-PAT-001``. It answers “Who does this blood sample belong to?”

* **Start at the patient.** The schema's ``backref: bloods`` names the
  reverse direction. Since ``root: patient`` starts Tube at the patient,
  ``path: bloods`` takes it from ``SYN-PAT-001`` back to ``SYN-BLD-001``.
  It answers “Which blood samples belong to this patient?”

Follow one blood sample through ETL
-----------------------------------

1. **The schema gives the rule.** A blood record must link to a patient
   through the ``patients`` field.
   See `blood.yaml <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/sample-data-dict/output-schema/blood.yaml#L25>`_.

2. **The submission supplies the link.** Blood sample ``SYN-BLD-001`` names
   patient ``SYN-PAT-001`` in its ``patients`` field. Gen3 checks the submission
   against the schema and saves the record and its link in PostgreSQL.
   See `blood.json <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/sample-data/blood.json#L3>`_.

3. **Start with each patient.** Line 34 in ``gen3-values.yaml`` says
   ``root: patient``. Here, *root* means the starting record type. Tube
   calculates the counts separately for each patient. In your sample data,
   it does this for ``SYN-PAT-001`` and again for ``SYN-PAT-002``.
   See `the starting rule <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/gen3-deployment/config/gen3-values.yaml#L34>`_.

4. **Follow the blood links and count the records.** Lines 42–44 of the
   same patient mapping give Tube the blood count rule.
   See `the count rule <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/gen3-deployment/config/gen3-values.yaml#L42-L44>`_.

   .. literalinclude:: ../../../../gen3-deployment/config/gen3-values.yaml
      :language: yaml
      :lines: 42-44
      :dedent: 10

   * ``path: bloods`` tells Tube where to look. From ``SYN-PAT-001``, it
     follows the saved link back to blood sample ``SYN-BLD-001``.

   * ``fn: count`` tells Tube what to do with the records it finds.
     It finds one linked record, so the result is ``1``.

   * ``name: _blood_count`` tells Tube what to call the result. Tube writes
     ``_blood_count: 1`` into the search entry for ``SYN-PAT-001`` in
     Elasticsearch, where the Explorer can show it.

What ETL counts for each patient
--------------------------------

**Submitting the records creates the links. ETL follows those saved links
and counts the records it finds.** For example, submitting ``SYN-BLD-001``
links it to ``SYN-PAT-001``. ETL finds that blood sample and saves a blood
count of one in the patient's search entry.

Your patient mapping counts blood samples and urine samples linked directly
to the patient. It also counts DNA records and sequencing runs by following
links through the patient's blood samples.
See `the four count rules <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/gen3-deployment/config/gen3-values.yaml#L41-L53>`_.

For example, plasma record ``SYN-PLA-001`` is linked to blood sample
``SYN-BLD-001``. That connection is saved at submission. Since the patient
mapping has no plasma count rule, the patient's search entry has no plasma
count.
See `the plasma submission <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/sample-data/plasma.json#L3-L10>`_.

How the Explorer uses the counts
--------------------------------

Open **Explorer → Patients**. Your portal is configured to show each
patient's blood sample count and sequencing run count in the table. You can
see how many blood samples belong to ``SYN-PAT-001`` without opening the
individual sample records and counting them yourself.
See `the Patients tab configuration <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/gen3-deployment/config/gen3-values.yaml#L528-L538>`_.

Tube calculates the counts for each patient when you run the search refresh
and saves them in Elasticsearch. When you open the Patients tab, the portal
asks Guppy, the Gen3 service that reads those saved search entries, for the
results. That's how ``_blood_count: 1`` becomes the number you see beside
``SYN-PAT-001``.
See `the Guppy configuration <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/gen3-deployment/config/gen3-values.yaml#L357-L372>`_.

If you submit a second blood sample for ``SYN-PAT-001``, Gen3 saves that new
link during submission. The next time you run the search refresh, the same
ETL mapping counts both samples and the Explorer can show **2**.
See `the search refresh playbook <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/gen3-deployment/03-refresh-search.yaml>`_.

How ETL also prepares the Files tab
-----------------------------------

Your ETL mapping builds two kinds of search entries for the Explorer.

* **Patients.** Tube saves a summary for each patient with the patient ID,
  project, and counts. For ``SYN-PAT-001``, the blood count answers
  “How many blood samples belong to this patient?”
* **Files.** Tube makes a searchable entry for ``synthetic-demo.fastq`` by
  copying details such as its filename and size from the sequencing-run
  record. This entry helps answer “Which sequencing file is associated with
  this patient?”

Imagine you see ``synthetic-demo.fastq`` in the Files tab and ask **“Whose
sample did this file come from?”** Start with ``SYN-SEQRUN-001``, the record
your registration script submits to describe the uploaded file. It gives
Gen3 the filename and size and says which DNA sample the run used.
See `the file registration script <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/src/03-register_sample_metadata.py#L41-L50>`_.

Tube follows three links that were saved during submission.

1. **Sequencing run → DNA.** The run ``SYN-SEQRUN-001`` used ``SYN-DNA-001``.
2. **DNA → Blood.** The DNA ``SYN-DNA-001`` came from blood sample
   ``SYN-BLD-001``.
3. **Blood → Patient.** The blood sample ``SYN-BLD-001`` belongs to patient
   ``SYN-PAT-001``.

The mapping says ``path: dnas.bloods.patients``. Each dot means “follow the
next link.” Tube saves a search entry with the filename, size, and patient
association. The Files tab uses the search entry to list the file, and the
FASTQ itself stays in MinIO.
See `the file mapping <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/gen3-deployment/config/gen3-values.yaml#L54-L79>`_.
