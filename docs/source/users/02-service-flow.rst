Which Gen3 Services Handle My Data?
===================================

User actions pass through different services. A file's bytes, its Indexd
entry, and its graph metadata are separate records. Uploading bytes alone
does not make a file visible in Exploration.

.. list-table:: User actions and the services involved
   :header-rows: 1
   :widths: 23 32 45

   * - Action
     - Services
     - What happens
   * - Browser login
     - Data Portal, Fence, Dex, LDAP
     - In this deployment Fence uses Dex as the identity provider; Dex checks the LDAP account.
   * - API authentication
     - Fence
     - The SDK exchanges the saved API credential for an access token.
   * - Permission checks
     - Arborist
     - Gen3 services check the user's allowed actions on resources such as
       ``/programs/training/projects/demo``.
   * - Push structured metadata
     - Sheepdog, PostgreSQL
     - Sheepdog validates nodes and links against the data dictionary and
       writes them to the graph database.
   * - Push file bytes
     - Fence, Arborist, Indexd, MinIO
     - Fence authorises the upload and returns a GUID and presigned URL.
       Indexd tracks the object; the client sends bytes directly to MinIO.
   * - Register uploaded file metadata
     - Indexd, Sheepdog, PostgreSQL
     - The example finalises size/checksum/location in Indexd and submits
       a ``seqrun`` node linked to its DNA parent through Sheepdog.
   * - Pull graph metadata
     - Peregrine, PostgreSQL
     - Peregrine translates GraphQL queries into queries over the graph.
       Sheepdog also provides metadata export endpoints.
   * - Search in Exploration
     - Tube, Elasticsearch, Guppy
     - An operator refreshes the search data with Tube; Guppy serves queries
       over that transformed representation.
   * - Pull file bytes
     - Fence, Arborist, Indexd, MinIO
     - Indexd resolves the GUID to its storage location. Fence checks access
       and provides a presigned URL; the client downloads from MinIO.

**Fence** is the authentication and file-access service in these examples.
**Peregrine** retrieves graph metadata. **Sheepdog** validates and stores graph metadata. **Indexd** tracks file
If you encounter **Fluent** in infrastructure settings, it refers to log collection for operators, rather than the 
token or file-transfer service.

The SDK wraps the HTTP APIs. A token identifies your session, while permissions
still determine which projects and files you can access. See the
:doc:`component guide </overview/components>` for the individual services.

Service descriptions are based on the `Gen3 microservices guide
<https://gen3.org/resources/developer/microservice/>`_ and `data-service
configuration guide
<https://docs.gen3.org/gen3-resources/operator-guide/helm/helm-config/helm-config-data-svcs/>`_.
The scripts in ``src/`` determine the specific local workflow described here.
