Log in to the Gen3 Portal
=========================

Use the portal address supplied by your operator. For this repository's local
training environment, open `http://gen3.kind.test <http://gen3.kind.test>`_.

#. Select **Login** and choose **Training LDAP**.
#. Complete the Dex login form using your training LDAP account.
#. After returning to Gen3, check that your profile shows the expected user.
#. Open **Profile** to create API credentials as described in
   :doc:`/users/api-credentials/01-gen-token`.

Which services handle login?
----------------------------

The **Data Portal** provides the login button. **Fence** redirects your browser
to the configured identity provider, **Dex**, which checks your credentials
against **LDAP**. After sign-in, Fence establishes your Gen3 session and issues
tokens. **Arborist** evaluates permissions when services check whether you can
access a project or perform an action. Successful login does not by itself
grant upload or download permission.

This is portal authentication. Kubernetes administration access is covered in
the :doc:`operator stream </operators/kubernetes-access/01-login>`.

Next, read :doc:`02-service-flow` and install the SDK before creating an API
credential for the examples.
