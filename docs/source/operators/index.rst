Operators
=========

Follow this stream to provision infrastructure, deploy Gen3, and maintain
identity, access policies, persistent storage, and search. Choose the local
training deployment or the OpenStack infrastructure path for your environment.

The local guide documents the current HTTP training environment. For an HTTPS
deployment, configure ingress certificates and the matching identity-provider
redirect URLs as part of the deployment configuration.

.. toctree::
   :maxdepth: 2

   /operators/local-deployment/index
   /operators/infrastructure/index
   /operators/kubernetes-access/01-login
   01-refresh-search

Kubernetes login is an administration task; portal login and API credentials
are in the :doc:`user stream </users/index>`. Obtain a validated dictionary
from a :doc:`data manager </data-managers/index>` before deploying Gen3.
