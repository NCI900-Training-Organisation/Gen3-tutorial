
- Every Gen3 data commons employs a data model, which serves to describe, organize, and harmonize structured data.

- Data harmonization is the process of combining different, mismatched datasets from various sources and organizing them into a single, clean, and consistent format

- Data harmonization facilitates cross-project analyses and is thus one of the pillars of the data commons paradigm

- The data model organizes experimental or clinical variables, “properties”, into linked categories, “nodes”, through the use of a data dictionary.

- The data dictionary lists and describes all nodes in the data model, as well as defines and describes the properties in each node

- In GEN3 there is yaml per node.

-  A dictionary needs to be defined to allow submission of structured metadata and use of the Exploration Page in the Data Portal.

- For example if a clinical experimaent have a variables `cancer digonisis` it may go into a node  `digonisis` while a variable `gender` may go into a node `demographic`.

- Similarly, we can organise metadata as well. For instance Data files may have metadata variables like file size, format, and filename. These properties can be grouped into nodes that describe various types of data files, like "mri_image", for an MRI image data file.

- Each node in the data dictionary is linked in a logical manner to other nodes (DAG), which facilitates generating a visual overview, or graphical model, of a project.

Node Catogories in the Dictionary
------------------------------------

- Administrative
    * The `Project`, `Study`, and `Subject` nodes are administrative nodes that are required for any Gen3 data commons. 
    * Administrative nodes store basic project and study information for their associated cases or subjects.
    * the Subject node level is where the nodes start differentiating between commons. 

- Clinical
    * Subject node links to the Demographic and Diagnosis clinical nodes
    * store clinical and medical history related data.
    * Demographic
        - stores properties that represent the statistical characterization of human populations
        - do notc usually change over time
    * Diagnosis
        - represents the investigation, analysis, and recognition of the presence and nature of disease, condition, or injury from expressed signs and symptoms. 
        - It also pertains to the scientific determination of any kind and the concise results of such an investigation.

- Biospecimen
    * 





