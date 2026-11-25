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

* **props.** These are the fields Tube copies directly into a search
  entry. Think of a simple field as a possible table column. The portal
  can choose to show it or use it as a filter. A field can also be renamed.
  Your patient mapping uses ``src: id`` to save Gen3's internal patient ID
  under the name ``_patient_id``.

  .. note::

     ``id`` is a built-in Gen3 field listed under ``systemProperties`` in
     the patient schema. Gen3 assigns it when it creates the record.
     The person submitting the record supplies ``submitter_id``.

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
     * ``path: urines`` comes from ``backref: urines`` in
       `urine.yaml <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/sample-data-dict/output-schema/urine.yaml#L25-L31>`_.

     The mapping uses these reverse names because ``root: patient`` tells
     Tube to start at the patient.

* **flatten_props.** This copies fields from a linked lower-level record.
  Your mapping has no ``flatten_props``. Gen3 shows both a one-to-one
  example and an example with several linked events where sorting by date
  lets Tube take fields from the most recent event.

* **aggregated_props.** This summarizes linked records. Your patient
  mapping uses ``path: bloods`` and ``fn: count`` to count the blood
  records for each patient. The other rules count urine samples, DNA records,
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
  ``project_id``. Those fields associate each file search entry with its patient.

.. note::

   A dot separates successive links. Read ``dnas.bloods.patients`` from
   left to right. Each step starts at the record found in the previous step.

   1. ``dnas`` follows the link from the sequencing run to DNA.
   2. ``bloods`` follows the link from DNA to blood.
   3. ``patients`` follows the link from blood to the patient.

   Tube copies the selected patient fields into the file search entry.

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

What ETL counts for each patient
--------------------------------

The patient mapping counts blood and urine records linked directly to
each patient. It also counts DNA records and sequencing runs by following
links through the patient's blood records. The mapping has no plasma count.
See `the four count rules <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/gen3-deployment/config/gen3-values.yaml#L41-L53>`_.

The blood count rule shows how the path, operation, and output name fit
together.

.. literalinclude:: ../../../../gen3-deployment/config/gen3-values.yaml
   :language: yaml
   :lines: 42-44
   :dedent: 10

For each patient, Tube follows ``bloods``, counts the records it finds, and
writes the result as ``_blood_count`` in the patient search entry.

How the Explorer uses the counts
--------------------------------

Open **Explorer → Patients** to see each patient's blood sample count
and sequencing run count. Guppy reads those values from Elasticsearch.
The counts update after the next ETL run.
See `the search refresh playbook <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/gen3-deployment/03-refresh-search.yaml>`_.

How ETL prepares the Files tab
------------------------------

The file mapping copies fields such as filename and size from each
sequencing-run record. Tube follows ``dnas.bloods.patients`` and adds the
patient association to the search entry. Guppy reads that entry for
**Explorer → Files**. The file itself stays in MinIO.
See `the file mapping <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/gen3-deployment/config/gen3-values.yaml#L54-L79>`_.
