Fence
-----

``Fence`` is an authentication and authorization service that uses the OpenID
Connect flow to generate tokens for clients. It can also provide tokens directly
to a user. Clients and users may then use those tokens with other Gen3 Data
Commons services to access protected endpoints that require specific permissions.

For instance, to access data and use it in a Jupyter notebook, you would need to
obtain a token from ``Fence`` and then use that token to access the data through the
``Data Portal`` or other Gen3 services.
