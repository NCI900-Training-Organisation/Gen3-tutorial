Build a Jumpbox
===============

The Talos control node can also be used as a jumpbox for managing the Gen3
environment and its Kubernetes cluster. Complete the Gen3 project provisioning
steps before starting this procedure.

This guide uses ``nd36`` and the ``train`` environment as examples. Replace
project names, network details, usernames, image versions, and credentials
with the values for your environment. The example CIDRs and IP addresses must
be checked against the addresses assigned to your project.

Procedure
---------

#. Reserve a floating IP for the jumpbox.
#. Create an SSH security group for approved NCI staff networks.
#. Create an OpenStack application credential for the Cinder CSI driver.
#. Add a jumpbox host to the Ansible inventory.
#. Create the Ansible variables and encrypted vault files.
#. Generate the SSH host keys required by the build.
#. Run the Ansible playbook to create the Talos control node.
#. Test SSH access and lock the instance.

Reserve a Floating IP
---------------------

Reserve a public floating IP in the OpenStack dashboard or with the OpenStack
CLI, then associate it with the jumpbox. Record the address; it is used in the
inventory and SSH configuration below. This example uses ``130.56.247.37``.

Create SSH Security Rules
-------------------------

The SSH security group allows connections to TCP port 22 from approved source
networks. The following CIDRs are examples; confirm the allowed NCI staff
networks with your cloud administrators before creating rules. Restricting the
source ranges is preferable to allowing SSH from the entire internet.

+------------------+-------------+------------+-----------+
| Source CIDR      | IP Protocol | Port Range | Direction |
+==================+=============+============+===========+
| 10.1.6.0/24      | TCP         | 22         | Ingress   |
+------------------+-------------+------------+-----------+
| 150.203.248.0/24 | TCP         | 22         | Ingress   |
+------------------+-------------+------------+-----------+

Create the security group and its ingress rules. Adjust the source CIDRs if
the approved network ranges for your environment differ:

.. code-block:: console

	openstack security group create ssh-nci-staff-only --description "NCI Staff SSH to Jumpbox"
	openstack security group rule create --protocol tcp --ethertype IPv4 --remote-ip 10.1.6.0/24 --dst-port 22 --ingress ssh-nci-staff-only
	openstack security group rule create --protocol tcp --ethertype IPv4 --remote-ip 150.203.248.0/24 --dst-port 22 --ingress ssh-nci-staff-only

The first command creates the ``ssh-nci-staff-only`` security group. Each
following command adds an ingress rule allowing TCP traffic on port 22 from
one approved CIDR. Replace the example CIDRs with the ranges approved for your
environment; keeping them specific limits SSH access to those networks.

Create an Application Credential
--------------------------------

The Cinder Container Storage Interface (CSI) driver uses an OpenStack
application credential to authenticate when managing persistent volumes.

.. note::
	
	OpenStack Cinder provides block storage volumes. In Kubernetes, the Cinder CSI
	driver lets workloads request persistent volumes backed by Cinder, and the
	application credential allows the driver to manage those volumes through the
	OpenStack API.

Create the credential in the OpenStack dashboard or with the CLI:

.. code-block:: console

	openstack application credential create --description "nd36 credential for csi" nd36_cinder_csi

Save the returned ID and secret in the Ansible vault described below. Store a
copy in the approved password manager, such as a 1Password entry tagged
``Gen3/<environment-name>`` (for example, ``Gen3/gen3-train``). The secret is
shown only when the credential is created, so save it securely at that time.

Prepare the Ansible Inventory
-----------------------------

The control node is built with Ansible code in the
`VL infrastructure management repository <https://git.nci.org.au/nci-vl/vl-infra-mgmt>`_.
Clone the repository and create a branch for your environment's inventory
change. Use an existing Gen3 inventory, such as
``inventories/kf17-dev-k8s.yaml``, as a starting point and adapt the values.

The example below is for project ``nd36``, network ``10.162.0.0/24``, internal
address ``10.162.0.3``, and floating IP ``130.56.247.37``. Use the Talos
release that matches the cluster you intend to manage.

.. code-block:: yaml

	---
	all:
	  vars:
	    vl_current_project: nd36
	    vl_os_service_name: nd36-k8s
	    vl_os_is_core_service: 0
	    vl_os_environment: train
	    vl_os_access_allow: "(cloud_admin)"
	    vl_os_sudo_allow: "cloud_admin"
	    vl_os_network: nd36
	    talosctl_release: v1.13.9
	  children:
	    jumpbox:
	      hosts:
	        nd36-train-talosctl:
	          vl_os_startup_phase: 1
	          vl_os_flavor: c3ep.4c8m20d
	          vl_os_ip: 10.162.0.3
	          vl_os_floating_ips:
	            - 130.56.247.37
	          vl_os_security_groups:
	            - default
	            - ssh-nci-staff-only
	          vl_os_image: Ubuntu Noble Server 2025-08-05

Create the Ansible Variables File
---------------------------------

Create a variables file for environment-specific settings. Set the SSH
username and point ``vl_ssh_pubkey`` to the public key that should be installed
for access to the jumpbox.

.. code-block:: yaml

	vl_os_key_name: dxp999
	vl_ssh_user: dxp999
	tl_ssh_user: dxp999
	vl_ssh_pubkey: "{{ lookup('file', '/home/me/.ssh/id_ed25519.pub') }}"
	vl_os_region: CloudV3
	vl_os_volume_type: Nirin2_Transaction
	vl_os_auth_url: https://cloud.nci.org.au:5000
	pause_for_ssh_copy_id: false

Update the example username, public-key path, region, and volume type to match
your environment. Keep the variables file separate from the encrypted vault:
it contains configuration, while the vault holds secrets.

Create the Ansible Vault File
-----------------------------

Create an Ansible Vault file for secrets required by the jumpbox and Talos
cluster builds. The exact variable names should match those expected by the
Ansible roles in the infrastructure repository. Typical values include:

* Gen3 Sectigo acme credentials for SSL certificate requests.
* The S3 access key created earlier, so that Talos etcd snapshots can be uploaded to S3.
* An age key we created earlier.
* The Cinder CSI application credential ID and secret created earlier.
* SSH Public and private keys to use for the build (TODO).
* The NCI nfcacert data.

.. note::

	Sectigo is a certificate authority that issues SSL/TLS certificates. The
	Gen3 Sectigo ACME credentials are controlled by the Cloud Team at NCI.

	The ``nfcacert`` value is a certificate specific to the NCI LDAP service.
	Approved certificate data controlled by the Cloud Team at NCI.

Confirm with the playbook maintainers which SSH keys are required. SSH client
keys used to log in and SSH host keys presented by the jumpbox serve different
purposes and should not be mixed up.

Create or edit the encrypted vault using the approved local process. The
following is a placeholder example only; replace each value and use the
project-specific variable names expected by the playbooks:

.. code-block:: yaml

	gen3_acme_eab_kid: REPLACE_WITH_ACME_KEY_ID
	gen3_acme_eab_key: REPLACE_WITH_ACME_SECRET
	s3_backup_access_key: REPLACE_WITH_S3_ACCESS_KEY
	s3_backup_secret_key: REPLACE_WITH_S3_SECRET_KEY
	etcd_snapshot_age_key: REPLACE_WITH_AGE_KEY
	nd36_cinder_csi_app_cred_id: REPLACE_WITH_APPLICATION_CREDENTIAL_ID
	nd36_cinder_csi_app_cred_secret: REPLACE_WITH_APPLICATION_CREDENTIAL_SECRET
	tl_ssh_user: REPLACE_WITH_LDAP_USERNAME
	tl_ssl_ingress_email: REPLACE_WITH_CONTACT_EMAIL
	nfcacert: |
	  -----BEGIN CERTIFICATE-----
	  REPLACE_WITH_APPROVED_CERTIFICATE_DATA
	  -----END CERTIFICATE-----

Do not put real passwords, access keys, private keys, or unencrypted vault
contents in source control, chat, or build logs.

Generate SSH Host Keys
----------------------

The ``vl-team-infra`` base-server build requires SSH host keys so the
jumpbox's identity is known during the Ansible build. Generate a private and
public key pair for each algorithm required by the playbook: ECDSA, RSA, and
Ed25519. Confirm the required algorithms with the playbook maintainers.

Generate the key pairs with commands like these:

.. code-block:: console

	ssh-keygen -t ed25519 -N "" -f ./ssh_host_ed25519_key
	ssh-keygen -t ecdsa -b 521 -N "" -f ./ssh_host_ecdsa_key
	ssh-keygen -t rsa -b 4096 -N "" -f ./ssh_host_rsa_key

Store only the key material required by the playbook in the Ansible vault.
Use the exact variable names expected by the roles, with the project name as
the prefix where required. The following illustrates the format for one key
pair; replace the placeholders with the contents of the matching key files
and add entries for the other required algorithms:

.. code-block:: yaml

	nd36_host_rsa_public: REPLACE_WITH_CONTENTS_OF_ssh_host_rsa_key.pub
	nd36_ssh_privkey: |
	  -----BEGIN OPENSSH PRIVATE KEY-----
	  REPLACE_WITH_CONTENTS_OF_ssh_host_rsa_key
	  -----END OPENSSH PRIVATE KEY-----

Keep private keys secret and store them only in the encrypted vault. Never
commit private keys or place them in ``known_hosts``.

The ``known_hosts`` file records public host keys, not private keys. The
commands below are retained from the original instructions, but they read the
private key files (without the ``.pub`` suffix), so do not run them to create
``known_hosts`` entries. Use the matching public key data from each ``.pub``
file, in the format ``hostname key-type public-key``. Confirm the required
host-key variables and setup procedure with the playbook maintainers.

.. code-block:: console

	echo "130.56.247.37 $(cat ./ssh_host_ecdsa_key)" >> .ssh/known_hosts
	echo "130.56.247.37 $(cat ./ssh_host_rsa_key)" >> .ssh/known_hosts
	echo "130.56.247.37 $(cat ./ssh_host_ed25519_key)" >> .ssh/known_hosts
	
	
After verifying that the public keys and fingerprints match those installed
by the build, remove local key files only after confirming that the required
private keys are safely stored in the encrypted vault. Follow your
organization's approved key-handling process; do not delete the only
recoverable copy.


Build the Talos Control Node
---------------------------

Source the OpenStack credentials for the project:

.. code-block:: console

	source nd36-openrc.sh

From the cloned ``vl-infra-mgmt`` repository, run the playbook using the
inventory, variables file, and encrypted vault created above. Keep the paths
and inventory filename consistent with the files you created for this
environment:

.. code-block:: console

	ansible-playbook --ask-pass --ask-become-pass --ask-vault-pass -e@~/ansible-common/nd36-train-k8s-vars.txt -e@~/ansible-vaults/gen3-train-k8s.vault -i inventories/nd36-train-k8s.yaml build-talosctl.yaml

Run this command from the root of the cloned ``vl-infra-mgmt`` repository.
The options and arguments are:

* ``--ask-pass`` prompts for the SSH login password when the playbook connects
	to hosts.
* ``--ask-become-pass`` prompts for the privilege-escalation password when a
	task uses Ansible ``become``.
* ``--ask-vault-pass`` prompts for the password that decrypts the Ansible
	vault file.
* ``-e@...vars.txt`` and ``-e@...vault`` load the environment-specific
	variables and encrypted secrets. Replace these example paths with the
	locations of your files.
* ``-i inventories/nd36-train-k8s.yaml`` selects the inventory describing the
	jumpbox and its environment.
* ``build-talosctl.yaml`` is the playbook to execute.

The prompts are separate: the login, privilege-escalation, and vault passwords
may differ. Use the authentication method and options required by your
environment.

Test SSH Access
---------------

After the playbook completes, connect to the floating IP with your NCI LDAP
900 account and password, or with the configured private client key. For
example:

.. code-block:: console

	ssh dxp999@130.56.247.37

You can add a local hosts-file entry or an SSH config entry to make the
jumpbox easier to address. An SSH config entry can also set the username so
you do not need to include it in every SSH command. Install any preferred
interactive shell tools after access is confirmed.

Lock the Jumpbox Instance
-------------------------

Lock the server to reduce the chance of accidental deletion or modification:

.. code-block:: console

	openstack server lock nd36-train-talosctl

Locking restricts actions such as deleting or modifying the server through
OpenStack, helping prevent accidental changes. It does not stop the instance;
authorized administrators may still be able to perform locked actions.