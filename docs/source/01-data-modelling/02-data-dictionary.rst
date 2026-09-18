Data Dictionary Overview
==============================

GEN3 uses a graph model to represent the data model.

In this model, each `entity` is represented as a `node` in the graph, and the `relationships` 
between entities are represented as `links` connecting the nodes. 

A single node (entity) can represented as a single yaml file called a `Gen3 Schema`
which is in the `jsonschema draft-04 format <https://json-schema.org/draft-04/draft-zyp-json-schema-04>`_.

This means that GEN3 graph model (data model) can be represented as a collection of `Gen3 Schema` files that are connected to each other through `links` (relationships) 
or a single json file.



.. note::

    1. **Gen3 Schema**: A single yaml or json file that defines a single node in the data model.

    2. **Gen3 Data Dictionary**: A folder containing multiple yaml files for each node in the data model.

    3. **Gen3 Bundled Schema**: A json file containing a dictionary of jsonschemas for each node in the data model.


    All dictionaries in Gen3 must have the following schemas

    1. Program
  
    2. Project
    
    3. Core Metadata Collections



Individual Schemas in Gen3 are will eventually be be compiled into a single json file that 
is used as the data dictionary for a given gen3 instance. Schemas are generally structured into three parts:

- **Descriptors** - fields that describe the schema itself
- **Links** - how this schema links to other schema in the data model
- **Properties** - the fields or attributes of the schema 


.. note::

    Mental model for GEN3 dictionary Vs generic datamodel:

    * schema = node = entity  

    * Links = relationships

    * properties = attributes

Gen3SchemaDev
-----------------

We will be using the `Gen3SchemaDev <https://github.com/AustralianBioCommons/gen3schemadev>`_ tool to create the data dictionary for our 
example data model. 



`Gen3SchemaDev` requires a high level YAML file where you can define the major components of your data model- ``input.yaml``. 
This file abstracts away some of the complexity and formatting needed for creating gen3 schemas.


In this file you can define the major components of your data model, including:

- nodes
- links
- properties

First lets start by adding a version and url to the ``input.yaml`` file.

.. code-block:: yaml

    version: 0.1.0
    url: https://link-to-data-portal

.. note::

    In practice the URL will be a link to an S3 bucket.


Next we will define the `nodes` in our data dictionary. In our example we have the following nodes in the data model: 
`Patient`, `Blood`, `Urine`, `Plasma`, `DNA`, and `SeqRun`. 


.. code-block:: yaml

    version: 0.1.0
    url: https://link-to-data-portal

    nodes:
      - name: program
      - name: project
      - name: patient
      - name: blood
      - name: urine
      - name: plasma
      - name: dna
      - name: seqrun

Then we add node categories to the data dictionary. Each node must have a category. The category is used to classify the node into a specific type.
The categories are:

* administrative
* analysis
* biospecimen
* clinical
* data_file
* metadata_file
* notation
* index_file
* clinical_assessment
* medical_history
* data_observations
* experimental_methods
* subject_characteristics
* imaging
* study_administration
* satellite
* radar
* stream_gauge
* weather_station

.. code-block:: yaml

    version: 0.1.0
    url: https://link-to-data-portal

    nodes:
      - name: program
        category: administrative
      - name: project
        category: administrative
      - name: patient
        category: clinical
      - name: blood
        category: biospecimen
      - name: urine
        category: biospecimen
      - name: plasma
        category: biospecimen
      - name: dna
        category: biospecimen
      - name: seqrun
        category: data_file


Then we add description to each node in the data dictionary.

.. code-block:: yaml

    version: 0.1.0
    url: https://link-to-data-portal

    nodes:
      - name: program
        category: administrative
        description: "Program node"
      - name: project
        category: administrative
        description: "Project node"
      - name: patient
        category: clinical
        description: "Patient node"
      - name: blood
        category: biospecimen
        description: "Blood sample node"
      - name: urine
        category: biospecimen
        description: "Urine sample node"
      - name: plasma
        category: biospecimen
        description: "Plasma sample node"
      - name: dna
        category: biospecimen
        description: "DNA specimen node"
      - name: seqrun
        category: data_file
        description: "Sequencing run node"

Now we add the properties of each node in the data dictionary.


.. code-block:: yaml

    version: 0.1.0
    url: https://link-to-data-portal

    nodes:
      - name: program
        category: administrative
        description: "Program node"
        properties:
          - name: db_gap_accession_number
            description: "The dbgap accession number provided for the program."
            type: string
      - name: project
        category: administrative
        description: "Project node"
        properties:
          - name: project_id
            description: "The project ID."
            type: string
      - name: patient
        category: clinical
        description: "Patient node"
        properties:
          - name: patient_id
            description: "The patient ID."
            type: string
      - name: blood
        category: biospecimen
        description: "Blood sample node"
        properties:
          - name: blood_id
            description: "The blood sample ID."
            type: string
          - name: patient_id
            description: "The patient ID."
            type: string
          - name: blood_type
            description: "The blood type."
            type: string
      - name: urine
        category: biospecimen
        description: "Urine sample node"
        properties:
          - name: urine_id
            description: "The urine sample ID."
            type: string
          - name: patient_id
            description: "The patient ID."
            type: string
      - name: plasma
        category: biospecimen
        description: "Plasma sample node"
        properties:
          - name: plasma_id
            description: "The plasma sample ID."
            type: string
          - name: blood_id
            description: "The blood sample ID."
            type: string
      - name: dna
        category: biospecimen
        description: "DNA specimen node"
        properties:
          - name: dna_id
            description: "The DNA ID."
            type: string
          - name: blood_id
            description: "The blood sample ID."
            type: string
          - name: dna_specimen_id
            description: "The DNA specimen ID."
            type: string
      - name: seqrun
        category: data_file
        description: "Sequencing run node"
        properties:
          - name: seqrun_id
            description: "The sequencing run ID."
            type: string
          - name: dna_id
            description: "The DNA ID."
            type: string


In a property, a specific data type called an enumeration (enum) can be used to specify a set of 
allowed values, like a controlled vocabulary. Enums are an array data type, where each value in the 
array is an allowed value.

For example we can add an enum to the `blood_type` property in the `Blood` node to specify the 
allowed blood types.

.. code-block:: yaml
    
  - name: blood
    category: biospecimen
    description: "Blood sample node"
    properties:
      - name: blood_id
        description: "The blood sample ID."
        type: string
      - name: patient_id
        description: "The patient ID."
        type: string
      - name: blood_type
        description: "The blood type."
        type: string
        enum:
          - "A+"
          - "A-"
          - "B+"
          - "B-"
          - "AB+"
          - "AB-"
          - "O+"
          - "O-"



Then we add the links between the nodes in the data dictionary.


.. code-block:: yaml

    version: 0.1.0
    url: https://link-to-data-portal

    nodes:
      - name: program
        category: administrative
        description: "Program node"
        properties:
          - name: db_gap_accession_number
            description: "The dbgap accession number provided for the program."
            type: string
      - name: project
        category: administrative
        description: "Project node"
        properties:
          - name: project_id
            description: "The project ID."
            type: string
      - name: patient
        category: clinical
        description: "Patient node"
        properties:
          - name: patient_id
            description: "The patient ID."
            type: string
      - name: blood
        category: biospecimen
        description: "Blood sample node"
        properties:
          - name: blood_id
            description: "The blood sample ID."
            type: string
          - name: patient_id
            description: "The patient ID."
            type: string
          - name: blood_type
            description: "The blood type."
            type: string
            enum:
              - "A+"
              - "A-"
              - "B+"
              - "B-"
              - "AB+"
              - "AB-"
              - "O+"
              - "O-"
      - name: urine
        category: biospecimen
        description: "Urine sample node"
        properties:
          - name: urine_id
            description: "The urine sample ID."
            type: string
          - name: patient_id
            description: "The patient ID."
            type: string
      - name: plasma
        category: biospecimen
        description: "Plasma sample node"
        properties:
          - name: plasma_id
            description: "The plasma sample ID."
            type: string
          - name: blood_id
            description: "The blood sample ID."
            type: string
      - name: dna
        category: biospecimen
        description: "DNA specimen node"
        properties:
          - name: dna_id
            description: "The DNA ID."
            type: string
          - name: blood_id
            description: "The blood sample ID."
            type: string
          - name: dna_specimen_id
            description: "The DNA specimen ID."
            type: string
      - name: seqrun
        category: data_file
        description: "Sequencing run node"
        properties:
          - name: seqrun_id
            description: "The sequencing run ID."
            type: string
          - name: dna_id
            description: "The DNA ID."
            type: string

    links:
      - parent: program
        multiplicity: one_to_many
        child: project
      - parent: project
        multiplicity: one_to_many
        child: patient
      - parent: patient
        multiplicity: one_to_many
        child: blood
      - parent: patient
        multiplicity: one_to_many
        child: urine
      - parent: blood
        multiplicity: one_to_one
        child: plasma  
      - parent: blood
        multiplicity: one_to_one
        child: dna
      - parent: dna
        multiplicity: many_to_one
        child: seqrun

By default every link is required, meaning a record cannot be submitted without it. 
Add `required: false` when a parent is optional. For example, if a patient can have a blood sample 
or a urine sample, but not necessarily both, we can make the link from patient to urine optional.

.. code-block:: yaml

    links:
      - parent: program
        multiplicity: one_to_many
        child: project
      - parent: project
        multiplicity: one_to_many
        child: patient
      - parent: patient
        multiplicity: one_to_many
        child: blood
      - parent: patient
        multiplicity: one_to_many
        child: urine
        required: false
      - parent: blood
        multiplicity: one_to_one
        child: plasma  
      - parent: blood
        multiplicity: one_to_one
        child: dna
      - parent: dna
        multiplicity: many_to_one
        child: seqrun


So the final ``input.yaml`` file for our example data model looks like this:

.. code-block:: yaml

    version: 0.1.0
    url: https://link-to-data-portal

    nodes:
      - name: program
        category: administrative
        description: "Program node"
        properties:
          - name: db_gap_accession_number
            description: "The dbgap accession number provided for the program."
            type: string
      - name: project
        category: administrative
        description: "Project node"
        properties:
          - name: project_id
            description: "The project ID."
            type: string
      - name: patient
        category: clinical
        description: "Patient node"
        properties:
          - name: patient_id
            description: "The patient ID."
            type: string
      - name: blood
        category: biospecimen
        description: "Blood sample node"
        properties:
          - name: blood_id
            description: "The blood sample ID."
            type: string
          - name: patient_id
            description: "The patient ID."
            type: string
          - name: blood_type
            description: "The blood type."
            type: string
            enum:
              - "A+"
              - "A-"
              - "B+"
              - "B-"
              - "AB+"
              - "AB-"
              - "O+"
              - "O-"
      - name: urine
        category: biospecimen
        description: "Urine sample node"
        properties:
          - name: urine_id
            description: "The urine sample ID."
            type: string
          - name: patient_id
            description: "The patient ID."
            type: string
      - name: plasma
        category: biospecimen
        description: "Plasma sample node"
        properties:
          - name: plasma_id
            description: "The plasma sample ID."
            type: string
          - name: blood_id
            description: "The blood sample ID."
            type: string
      - name: dna
        category: biospecimen
        description: "DNA specimen node"
        properties:
          - name: dna_id
            description: "The DNA ID."
            type: string
          - name: blood_id
            description: "The blood sample ID."
            type: string
          - name: dna_specimen_id
            description: "The DNA specimen ID."
            type: string
      - name: seqrun
        category: data_file
        description: "Sequencing run node"
        properties:
          - name: seqrun_id
            description: "The sequencing run ID."
            type: string
          - name: dna_id
            description: "The DNA ID."
            type: string

    links:
      - parent: program
        multiplicity: one_to_many
        child: project
      - parent: project
        multiplicity: one_to_many
        child: patient
      - parent: patient
        multiplicity: one_to_many
        child: blood
      - parent: patient
        multiplicity: one_to_many
        child: urine
        required: false
      - parent: blood
        multiplicity: one_to_one
        child: plasma  
      - parent: blood
        multiplicity: one_to_one
        child: dna
      - parent: dna
        multiplicity: many_to_one
        child: seqrun