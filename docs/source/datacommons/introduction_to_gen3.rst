Introduction to Gen3
====================

Gen3 is an open-source platform for building data commons, data meshes, data
hubs, and secure analysis workspaces. It helps research communities manage,
share, discover, and analyse data while retaining control over access.

Why Gen3?
---------

Sharing research data is difficult for several reasons:

* Researchers may have little incentive to share data after its original use.
* Incomplete or low-quality metadata can make data difficult to understand and
  reuse.
* Incompatible architectures, closed interfaces, and non-standard protocols
  can prevent systems from exchanging data.

Gen3 addresses these problems by combining data management, discovery, access
control, and analysis services in a secure platform. Operators decide how
public their systems and data should be, while open APIs and standard
protocols allow Gen3 deployments to interoperate.

FAIR data principles
~~~~~~~~~~~~~~~~~~~~

Gen3 is designed to support the FAIR data principles:

Findable
   Metadata and query services index data with unique, persistent identifiers
   and make the data searchable across resources.

Accessible
   Authentication and authorization services protect data, while a web portal
   lets authorized users explore projects and launch analysis workspaces.

Interoperable
   Open APIs use common protocols and formats so that Gen3 can communicate
   with other data resources.

Reusable
   Data models give contributors a shared vocabulary for clinical,
   phenotypic, biospecimen, and file metadata.

Gen3 products
-------------

Data commons
~~~~~~~~~~~~

A data commons places data management services alongside tools for data
exploration, analysis, and visualization. It can manage structured information,
such as clinical, phenotypic, and biospecimen data, as well as unstructured
objects such as genomic files and medical images. A data commons can also
interoperate with other resources in a data mesh.

``data.midrc.org`` is an example of a Gen3 data commons.

Data meshes and mesh services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A data mesh, also called a data ecosystem or data fabric, consists of two or
more data commons, repositories, knowledge bases, or applications that use a
common set of services. The mesh connects data held by its member nodes; it
does not need to move all data into one central location.

Mesh services provide open APIs for:

* indexing data objects;
* associating metadata with those objects; and
* controlling user access.

``healdata.org`` is an example of a Gen3 data mesh.

Data hubs
~~~~~~~~~

A data hub provides a single discovery interface or API for finding and
combining information across a data mesh. The hub stores persistent
identifiers, URLs, or other pointers to data, while the platforms that host the
files continue to manage access to them.

Workspaces
~~~~~~~~~~

Gen3 workspaces are secure cloud analysis environments that can access data
from one or more resources. The default workspace applications include
JupyterLab and RStudio, but operators can provide other applications, analysis
workflows, processing pipelines, and visualization tools.

Workspaces use Gen3 mesh services to authenticate and authorize users and to
retrieve data objects and metadata. Workspace images can contain different
software packages and tutorials, and operators can offer virtual machines with
different compute resources. A persistent drive retains a user's notebooks,
results, and other artifacts between sessions.

Core capabilities
-----------------

Data management
~~~~~~~~~~~~~~~

Gen3 manages three broad types of data:

Structured data
   Tables or JSON records that conform to a data model. The model harmonizes
   submitted data and defines links between related records. Structured data
   is used to build cohorts and identify files of interest.

Unstructured data
   Files stored in object storage or indexed in place. Each file receives a
   persistent identifier, such as a GUID, and can be downloaded or sent to an
   analysis environment when the user is authorized.

Semi-structured data
   Flexible JSON records that can contain nested fields without requiring a
   fixed hierarchy. Typical uses include dataset discovery metadata,
   privacy-preserving record linkage crosswalks, and package metadata.

Data access
~~~~~~~~~~~

Gen3 uses attribute-based access control to protect data, compute resources,
and user-interface components. ``Arborist`` is the policy engine. Access rules
can be maintained in YAML allowlists or synchronized with an external
authorization source.

Users can access data in several ways:

* Structured data is available through APIs, queries, the Exploration page,
  and table exports.
* Semi-structured metadata is available from the Discovery page, where related
  files can be downloaded or exported to workspaces.
* Files are retrieved by GUID through the portal's file endpoint, the Gen3
  Python SDK, or the ``gen3-client`` command-line tool.

Data search
~~~~~~~~~~~

``Peregrine`` and ``Guppy`` provide structured-data query capabilities.
Peregrine works with the PostgreSQL representation of the data model, while
Guppy queries data transformed into Elasticsearch. The Query page provides an
interactive query builder and schema viewer, and the Exploration page supports
faceted cohort building.

The metadata service searches semi-structured records by key-value pairs and
can support aliases used by crosswalk services. ``Indexd`` searches file
metadata by identifier; it does not search inside files.

Data analysis
~~~~~~~~~~~~~

Analysis features include:

* custom applications;
* a resource browser containing tutorials and example notebooks;
* JupyterLab and RStudio workspaces; and
* workflow and task execution services for running pipelines such as Nextflow.

Architecture and service flow
-----------------------------

Gen3 uses a flexible microservice architecture. Front-end components interact
with APIs, which use back-end services for data, policy, and processing. The
services can be deployed together or selected according to the use case.

A typical user journey is:

#. Discover relevant datasets.
#. Search structured data and select a cohort.
#. Manage cohort and user-specific information.
#. Send the selected data to an analysis environment.

The main services involved in this flow include:

``Metadata Service``
   Stores and searches flexible discovery metadata.

``Sheepdog``
   Validates structured submissions against the data model, reports validation
   errors, stores accepted records in PostgreSQL, and supports table exports.

``Peregrine``
   Exposes a GraphQL interface for querying structured data and relationships
   stored in PostgreSQL.

``Elasticsearch`` and ``Guppy``
   The ETL process extracts and transforms selected PostgreSQL data into an
   Elasticsearch index. Guppy provides a fast query layer over that index and
   supports the Exploration page.

``Indexd``
   Assigns and resolves persistent identifiers for files and their metadata.

``Fence``
   Manages login and selected data-access operations, often using an external
   identity provider as the source of truth.

``Arborist``
   Evaluates authorization policies and determines which resources a user may
   access.

``Revproxy``
   Directs incoming traffic to the appropriate service and has no front-end
   component of its own.

Deployment and operation
------------------------

Gen3 services are containerized and run on Kubernetes. A deployment can run in
a public cloud, on premises, or in another Kubernetes-capable environment.
Helm charts define the components and their dependencies, install them, manage
configuration values, and support upgrades and rollbacks.

Gen3 is released under the Apache License 2.0 and is implemented primarily as
Python and Go web services with REST APIs. The project publishes frequent
updates, so operators should validate release compatibility and configuration
before upgrading. See :doc:`../gen3` for this repository's deployment and
operations guides.

Security responsibilities
-------------------------

Gen3 provides authentication, authorization, access-control, and security
patching capabilities. The Center for Translational Data Science operates some
Gen3 environments under FedRAMP Moderate controls and follows a secure
development and operations process. This does not automatically make every
Gen3 deployment compliant. Each operator is responsible for selecting and
meeting the legal, institutional, and security requirements that apply to its
data and environment.

Contributing
------------

Community members can contribute by:

* submitting source-code changes through the appropriate Gen3 repository;
* improving the Gen3 technical documentation;
* reporting bugs or proposing features through GitHub issues; and
* participating in the Gen3 Slack community and Gen3 Community Forum.

Source material
---------------

This overview was prepared from the local ``Readme_data.md`` notes and the
*Introduction to Gen3* presentation delivered at the Gen3 Community Forum on
May 6, 2026.
