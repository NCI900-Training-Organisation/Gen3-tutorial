Understanding Gen3 and Its Components
=====================================

Learn how Gen3 services work together before following a role-based stream.
These services handle identity, permissions, metadata, file indexing, search,
and workspaces.

.. contents:: Components on this page
   :local:
   :depth: 1

.. figure:: /images/04-gen3-data-services.png
   :alt: Gen3 data architecture showing Peregrine and Guppy query services
   :align: center

   Gen3 services connect the portal to metadata, search, and data storage.


.. _gen3-component-arborist:

Arborist
--------

``Arborist`` is the Gen3 Policy Engine, an attribute-based access control (ABAC)
policy engine. It tracks resources requiring access control, along with actions
that users may perform on these resources and roles that aggregate permissions
to perform one or more actions.

Other services use ``Arborist`` for authorisation decisions, including API-level
access and permission to read or delete a specific indexed record. Services
should offload all authorisation-related logic to ``Arborist`` as much as possible.


.. _gen3-component-data-portal:

Data Portal
-----------

The ``Data Portal`` is a user-facing service in Gen3. It provides an interactive
website that allows users to explore, submit, and download data.


.. _gen3-component-fence:

Fence
-----

``Fence`` is an authentication and authorisation service that uses the OpenID
Connect flow to generate tokens for clients. It can also provide tokens directly
to a user. Clients and users may then use those tokens with other Gen3 Data
Commons services to access protected endpoints that require specific permissions.

For instance, to access data and use it in a Jupyter notebook, you would need to
obtain a token from ``Fence`` and then use that token to access the data through the
``Data Portal`` or other Gen3 services.


.. _gen3-component-guppy:

Guppy
-----

``Guppy`` supports GraphQL queries on data from Elasticsearch. It integrates with
``Arborist`` to filter out results that a user should not see.

``Guppy`` is an integral part of the ETL (Extract, Transform, Load) process in
Gen3. This is instrumental in querying data that has been indexed in
Elasticsearch.


.. _gen3-component-hatchery:

Hatchery
--------

Workspace services in Gen3 must expose HTTP servers. ``Hatchery`` creates Kubernetes
Pods for workspace services.


.. _gen3-component-indexd:

Indexd
------

The ``Indexd`` service provides permanent, digital, globally unique IDs (GUIDs) for
data objects. These IDs can be used to register the data, retrieve the data, or
query the metadata associated with the object.

``Indexd`` also tracks the locations and hash of every asset (file) in the data
commons object store. It provides an API for registering a new asset and
retrieving data for an existing asset.


.. _gen3-component-manifest-service:

Manifest Services
-----------------

A manifest is a JSON file that lists records a user may be interested in
analysing. The ``Manifest Service`` stores a manifest in a user folder in an S3
bucket and delivers it for later use.


.. _gen3-component-metadata-service:

Metadata Services
-----------------

The ``Metadata Service`` provides an API for retrieving JSON metadata of GUIDs.
This service powers the ``Data Portal`` Discovery Page for a Data Commons.


.. _gen3-component-peregrine:

Peregrine
---------

``Peregrine`` is the metadata-seeking service that responds to GraphQL search
queries. It translates them to queries over the graph-like PostgreSQL database
for structured data.

.. note::

    * ``Peregrine`` queries the complete PostgreSQL graph and is useful when a query depends on the original relationships.
    * ``Guppy`` queries the Elasticsearch representation and is useful for fast, repeated Explorer searches.


.. _gen3-component-requestor:

Requestor
---------

``Requestor`` exposes an API to manage access requests.
It supports workflows for requesting access to resources and tracking request status.
Its access-request workflow complements the permissions enforced by ``Arborist``.


.. _gen3-component-sheepdog:

Sheepdog
--------

The ``Sheepdog`` service manages user submissions of metadata into the graph
database. The submissions are quality controlled against the data dictionary to
ensure all required fields are present and have appropriate data values.
``Sheepdog`` also supports bulk export of the metadata into TSV or JSON formats.

.. note::

    * ``Sheepdog`` validates structured submissions against that model and stores the submitted graph in PostgreSQL.

    * ``Peregrine`` exposes the normalised graph through GraphQL.


.. _gen3-component-sower:

Sower
-----

``Sower`` dispatches Kubernetes jobs.
It launches configured tasks as container workloads rather than running them in the portal.
This allows background processing to run separately from interactive user requests.


.. _gen3-component-tube:

Tube
----

``Tube`` is a microservice that controls the ETL process of structured data.

.. note::

    - The data model defines the graph of nodes and relationships.
    - ``Sheepdog`` validates structured submissions against that model and stores the submitted graph in PostgreSQL.
    - ``Peregrine`` exposes the normalised graph through GraphQL.
    - ``Tube`` extracts selected graph data, transforms it according to the ETL mapping, and writes Elasticsearch documents.
    - ``Guppy`` queries those documents, and the Exploration page uses ``Guppy`` to provide filters, cohort searches, tables, and charts.


.. _gen3-component-workspace-token-service:

Workspace Token Service
-----------------------

The Gen3 ``Workspace Token Service`` (``WTS``) acts as an OIDC client on behalf of users
to request refresh tokens from ``Fence``. This happens when a user logs into a
workspace from the browser. ``WTS`` then stores the refresh token for that user and
manages access tokens and refresh tokens for workers that belong to specific
users in the workspace.
