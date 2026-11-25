Design the Gen3 training portal
===============================

Use the training portal as a starting point for designing an Explorer
around your data model. In this tutorial, you will trace an existing
column from ETL to the screen, then add a urine sample count to the
Patients table.

Work in ``gen3-deployment/config/gen3-values.yaml``. The portal settings
are in the JSON block under ``portal.gitops.json``. The same YAML file
also contains the Tube mapping and Guppy configuration.
See the `training configuration <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/gen3-deployment/config/gen3-values.yaml>`_.

Portal design configuration
---------------------------

This excerpt shows the ``gitops`` block under ``portal``, including the
homepage and navigation settings, feature flags, and both Explorer tabs.

.. literalinclude:: ../../../../gen3-deployment/config/gen3-values.yaml
   :language: yaml
   :start-at: gitops:
   :end-before: image:
   :dedent: 2

1. Decide what users should be able to find
-------------------------------------------

Write down a question for each tab and decide what one row represents.
Then choose fields users need to see and fields they need to filter by.
The training portal uses these two designs.

.. list-table::
   :header-rows: 1

   * - Tab and question
     - One row represents
     - Table columns
     - Filters
   * - **Patients.** What samples and sequencing runs are linked to a patient?
     - One patient
     - Patient ID, submitter ID, project, blood count, sequencing run count
     - Project and patient ID
   * - **Files.** Which sequencing files are available?
     - One sequencing file
     - Filename, size, data format, sequencing run ID
     - Project, data category, data type, and data format

For example, a user can filter the Patients tab by project and then read
the blood count in each row. A field can serve both purposes, as
``project_id`` does, or serve just one.

2. Connect each tab to the right search data
--------------------------------------------

Tube prepares the search entries and saves them in Elasticsearch.
Guppy gives the portal a label it can use to request those entries.
In each tab's ``guppyConfig``, ``dataType`` must match the ``type`` Guppy
uses for the intended index.

.. list-table::
   :header-rows: 1

   * - Tab
     - Index produced by Tube
     - Guppy ``type``
     - Explorer ``dataType``
   * - Patients
     - ``training_patient``
     - ``patient``
     - ``patient``
   * - Files
     - ``training_file``
     - ``file``
     - ``file``

To trace an existing column, find ``_blood_count`` in the patient ETL
mapping. Tube follows ``bloods`` and counts the linked records for each
patient. Then find ``_blood_count`` under ``table.fields`` in the Patients
tab. That entry tells the portal to display the indexed count.
See :doc:`../etl/01-etl` for how Tube builds the two indices.

3. Choose what the Explorer shows
---------------------------------

Find ``explorerConfig`` inside the JSON block. Each entry describes one tab.

* ``tabTitle`` is the tab's visible name.
* ``table.fields`` lists the indexed fields shown as columns, in order.
* ``filters.tabs[].fields`` lists fields offered in each filter group.
* ``charts`` specifies which fields to summarize above the table. The
  Patients tab shows patient and project counts. The Files tab uses a bar
  chart for data format.
* ``guppyConfig.fieldMapping`` gives selected fields human-readable names.
  For example, ``patient_id`` is labelled **Patient ID**.

For the pages around the Explorer, edit ``components.index`` for the home
page, ``components.navigation`` for navigation links, and
``components.login`` for sign-in instructions. The training portal
enables the Explorer through ``featureFlags.explorer``.

4. Try adding an existing field to the Patients table
-----------------------------------------------------

The patient mapping already calculates ``_urine_count``. In the
``Patients`` entry under ``explorerConfig``, add it after
``_blood_count`` in ``table.fields``. The updated table section would
look like this.

.. code-block:: json

   {
     "enabled": true,
     "fields": [
       "patient_id",
       "submitter_id",
       "project_id",
       "_blood_count",
       "_urine_count",
       "_seqrun_count"
     ]
   }

Keep the JSON indented inside the YAML block. Coordinate with your
operator to apply the updated portal configuration using the
:doc:`deployment guide </operators/local-deployment/01-local-deploy>`.
If the existing index already contains ``_urine_count``, the new column
only needs the portal configuration change. A new or changed ETL field
also needs the mapping deployed and the search index refreshed.

5. Verify the design in the portal
----------------------------------

1. Open **Exploration → Patients**. With the tutorial metadata indexed,
   find ``SYN-PAT-001`` using the patient ID filter. Confirm its urine
   count is **1** and its blood and sequencing run columns are still visible.
2. Open **Files**. If the tutorial's sequencing run has been registered
   and indexed, confirm that ``synthetic-demo.fastq`` appears with its file
   size and sequencing run ID.
3. If the new column is missing, check the deployed portal's
   ``table.fields`` first. If the column appears but has no value, check
   whether the field is in the index and whether search has been refreshed
   since the metadata was submitted.

To design another tab, repeat the same process with a new question.
Choose the row, check which fields the index provides, and add the
columns, filters, and charts that help users answer that question.

.. note::

   **Follow the blood count from the data model to the portal.**

   1. **Data model.** In ``input.yaml``, the relationship from ``patient``
      to ``blood`` is one-to-many. One patient can have several blood
      samples. See `the relationship in the data model <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/sample-data-dict/input.yaml#L88-L90>`_.
   2. **Generated schema.** In ``blood.yaml``, ``name: patients`` lets a
      blood submission point to its patient. The same link has
      ``backref: bloods`` so Tube can follow it from the patient back to
      the blood samples. Gen3 uses the bundled schema to check the
      submitted link. See `the generated blood schema <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/sample-data-dict/output-schema/blood.yaml#L25-L31>`_.
   3. **ETL field.** The mapping starts at ``root: patient``. It follows
      ``path: bloods``, uses ``fn: count``, and saves the result in
      Elasticsearch under ``name: _blood_count``. Tube creates this field
      when it runs. See `the blood count rule <https://github.com/NCI900-Training-Organisation/Gen3-tutorial/blob/HEAD/gen3-deployment/config/gen3-values.yaml#L41-L44>`_.
   4. **Portal design.** The Patients tab asks Guppy for ``patient``
      results and includes ``_blood_count`` in ``table.fields``. That
      setting makes the saved count a column in the table.

   For example, the submitted link from ``SYN-BLD-001`` to ``SYN-PAT-001``
   gives Tube one blood sample to count. After ETL runs, the Patients
   table can show **1** for that patient.
