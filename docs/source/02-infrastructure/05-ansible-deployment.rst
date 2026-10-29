Gen3 Deployment Repository
==========================

The Gen3 Ansible deployment repository is located at
``git.nci.org.au:nci-cloud/gen3-deploy.git``. Clone it locally and create a new
branch.

Deployed Components
-------------------

The Gen3 Ansible deployment playbook fully deploys the following components:

* StorageClasses to suit Gen3 and its database cluster
* The CloudNative PostgreSQL Operator to provision database clusters
* An Elasticsearch cluster
* The ArgoCD application
* Various Dex OIDC LDAP bridges
* The Gen3 PostgreSQL database cluster
* Monitoring subsystems
* Grafana dashboards
* The Gen3 deployment

Inventory
---------

To build a new Gen3 environment, you will first need to create an Ansible
inventory used to deploy the various components.

Use one of the existing inventories in the Gen3 deployment repository and create
one specific to your environment. The example below is for the training
environment. Many of the variables will relate to items provisioned in the
previous steps.

.. literalinclude:: gen3-deployment-inventory.yaml
   :language: yaml
   :caption: Example Gen3 deployment inventory
