Arborist
--------

``Arborist`` is the Gen3 Policy Engine, an attribute-based access control (ABAC)
policy engine. It tracks resources requiring access control, along with actions
that users may perform on these resources and roles that aggregate permissions
to perform one or more actions.

Other services use ``Arborist`` for authorisation decisions, including API-level
access and permission to read or delete a specific indexed record. Services
should offload all authorisation-related logic to ``Arborist`` as much as possible.
