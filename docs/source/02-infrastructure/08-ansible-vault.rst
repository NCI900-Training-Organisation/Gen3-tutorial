Ansible Vault
=============

Ansible Vault is Ansible's feature for encrypting sensitive data, such as
passwords, tokens, and certificates, so they can be stored in a file without
leaving the values readable as plaintext. Ansible decrypts the file when it
needs the values, using the vault password.

Deployment secrets for this environment are stored in an Ansible Vault file.
Create the vault directory if needed, then create the encrypted vault:

.. code-block:: console

	mkdir -p ~/ansible-vaults
	ansible-vault create ~/ansible-vaults/gen3-train-deploy.vault

When prompted, choose a vault password. The command opens an editor; add the
following YAML, replacing each placeholder with the value for this environment:

.. code-block:: yaml

	s3_access_key: "<base64-encoded S3 service account access key>"
	s3_secret_key: "<base64-encoded S3 service account secret key>"
	s3_host_base: "https://cloud.nci.org.au:8080"
	gen3_db_role_username: "<base64-encoded master Gen3 database username>"
	gen3_db_role_password: "<base64-encoded master Gen3 database password>"
	postgres_db_role_username: "<base64-encoded PostgreSQL admin username>"
	postgres_db_role_password: "<base64-encoded PostgreSQL admin password>"
	git_service_account: "<ArgoCD repository Git service account name>"
	git_service_account_token: "<Git service account token>"
	nfcacert: |
	  <paste the NCI LDAP certificate here>

The S3 access and secret keys, Gen3 database credentials, and PostgreSQL
administrator credentials must be base64 encoded before they are added. The
S3 URL shown above is the usual OpenStack endpoint; replace it if the
environment uses a different endpoint. For ``nfcacert``, replace the
placeholder with the complete NCI LDAP certificate, keeping its lines
indented under the ``|``. Do not commit the vault password or plaintext
secret values to the repository.

Vault values
------------

``s3_access_key``
	Base64-encoded S3 service account access key created during provisioning.

``s3_secret_key``
	Base64-encoded S3 service account secret key created during provisioning.

``s3_host_base``
	Base URL for the OpenStack S3 service, usually
	``https://cloud.nci.org.au:8080``.

``gen3_db_role_username`` and ``gen3_db_role_password``
	Base64-encoded master Gen3 database username and password.

``postgres_db_role_username`` and ``postgres_db_role_password``
	Base64-encoded PostgreSQL administrator username and password. The
	username is usually ``postgres``.

``git_service_account``
	Name of the Git service account for the ArgoCD repository.

``git_service_account_token``
	Token for the Git service account, created during ArgoCD repository
	configuration.

``nfcacert``
	NCI LDAP certificate.
