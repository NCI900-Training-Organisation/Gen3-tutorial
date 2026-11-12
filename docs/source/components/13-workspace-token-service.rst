Workspace Token Service
-----------------------

The Gen3 ``Workspace Token Service`` (``WTS``) acts as an OIDC client on behalf of users
to request refresh tokens from ``Fence``. This happens when a user logs into a
workspace from the browser. ``WTS`` then stores the refresh token for that user and
manages access tokens and refresh tokens for workers that belong to specific
users in the workspace.
