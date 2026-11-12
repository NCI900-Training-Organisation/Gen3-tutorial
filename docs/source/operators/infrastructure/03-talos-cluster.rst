Talos Kubernetes Cluster
================================

This guide describes the OpenStack setup and Ansible steps to build a Talos
Kubernetes cluster for a Gen3 environment. Complete the following guides
before starting:

The examples use the ``nd36`` project and ``gen3-train`` environment. Replace
project names, IP addresses, DNS names, LDAP groups, image versions, and
credentials with the values for your environment.

Procedure
---------

#. Create floating IPs for the ingress nodes and request a DNS record.
#. Create the required OpenStack security groups and ingress rules.
#. Create the object storage containers and server groups.
#. Register the DNS name for SSL certificate requests.
#. Create an inventory in the ``talos-k8s`` repository.
#. Run the Talos cluster playbook and verify the nodes.

Ingress Network Settings
------------------------

Create two external floating IPs for the two Kubernetes ingress nodes:

.. code-block:: console

	openstack floating ip create external
	openstack floating ip create external

Record both addresses. They are used as the public IPs of the ingress nodes in
the inventory. Request an A record from NCI network staff for the first
floating IP, for example ``gen3-train.nci.org.au``.

Security Groups
---------------

Create the security groups and ingress rules before building the cluster. The
rules below are the ingress rules required for the listed services; egress
rules are the OpenStack defaults. The security group names attached to each
node in the inventory must match the names created here.

``http-nci-staff-only``
~~~~~~~~~~~~~~~~~~~~~~~

Allows HTTPS access to the Gen3 portal from NCI staff networks and the router,
and HTTP access from the NCI staff network:

.. list-table:: Ingress rules
	:header-rows: 1
	:widths: 20 30 15 15 20

	* - IP Protocol
	  - IP Range
	  - Port Range
	  - Direction
	  - Notes
	* - TCP
	  - 130.56.245.149/32
	  - 443:443
	  - Ingress
	  - Router
	* - TCP
	  - 150.203.248.0/24
	  - 443:443
	  - Ingress
	  -
	* - TCP
	  - 10.1.6.0/24
	  - 443:443
	  - Ingress
	  -
	* - TCP
	  - 10.1.9.0/24
	  - 443:443
	  - Ingress
	  -
	* - TCP
	  - 150.203.248.0/24
	  - 80:80
	  - Ingress
	  -

``grafana-nci-staff-only``
~~~~~~~~~~~~~~~~~~~~~~~~~~

Allows access to Grafana at ``http://gen3-<env>.nci.org.au:3000`` from the
listed networks. The group also allows HTTPS from ``10.1.6.0/24``.

.. list-table:: Ingress rules
	:header-rows: 1
	:widths: 20 30 15 15 20

	* - IP Protocol
	  - IP Range
	  - Port Range
	  - Direction
	  - Notes
	* - TCP
	  - 10.1.6.0/24
	  - 3000:3000
	  - Ingress
	  -
	* - TCP
	  - 10.1.6.0/24
	  - 443:443
	  - Ingress
	  -
	* - TCP
	  - 130.56.245.149/32
	  - 3000:3000
	  - Ingress
	  - Router
	* - TCP
	  - 150.203.248.0/24
	  - 3000:3000
	  - Ingress
	  -

``ssh-nci-staff-only``
~~~~~~~~~~~~~~~~~~~~~~

Allows SSH access on TCP port 22 from the listed NCI staff networks. This
group is attached to the Talos controller node, which is built separately.

.. list-table:: Ingress rules
	:header-rows: 1
	:widths: 25 30 20 25

	* - IP Protocol
	  - IP Range
	  - Port Range
	  - Direction
	* - TCP
	  - 10.1.6.0/24
	  - 22:22
	  - Ingress
	* - TCP
	  - 150.203.248.0/24
	  - 22:22
	  - Ingress

``argocd-nci-staff-only``
~~~~~~~~~~~~~~~~~~~~~~~~~

Allows access to ArgoCD on TCP port 8443 from the listed NCI networks, the
jumpbox, and the router:

.. list-table:: Ingress rules
	:header-rows: 1
	:widths: 20 30 15 15 20

	* - IP Protocol
	  - IP Range
	  - Port Range
	  - Direction
	  - Notes
	* - TCP
	  - 10.1.6.0/24
	  - 8443:8443
	  - Ingress
	  -
	* - TCP
	  - 130.56.245.34/32
	  - 8443:8443
	  - Ingress
	  - Jumpbox
	* - TCP
	  - 130.56.245.149/32
	  - 8443:8443
	  - Ingress
	  - Router
	* - TCP
	  - 10.1.9.0/24
	  - 8443:8443
	  - Ingress
	  -
	* - TCP
	  - 150.203.248.0/24
	  - 8443:8443
	  - Ingress
	  -

Create the groups and rules with the OpenStack CLI:

.. code-block:: console

	openstack security group create http-nci-staff-only
	openstack security group rule create --protocol tcp --ethertype IPv4 --remote-ip 130.56.245.149/32 --dst-port 443 --ingress http-nci-staff-only
	openstack security group rule create --protocol tcp --ethertype IPv4 --remote-ip 150.203.248.0/24 --dst-port 443 --ingress http-nci-staff-only
	openstack security group rule create --protocol tcp --ethertype IPv4 --remote-ip 10.1.6.0/24 --dst-port 443 --ingress http-nci-staff-only
	openstack security group rule create --protocol tcp --ethertype IPv4 --remote-ip 10.1.9.0/24 --dst-port 443 --ingress http-nci-staff-only
	openstack security group rule create --protocol tcp --ethertype IPv4 --remote-ip 150.203.248.0/24 --dst-port 80 --ingress http-nci-staff-only

	openstack security group create grafana-nci-staff-only
	openstack security group rule create --protocol tcp --ethertype IPv4 --remote-ip 10.1.6.0/24 --dst-port 3000 --ingress grafana-nci-staff-only
	openstack security group rule create --protocol tcp --ethertype IPv4 --remote-ip 10.1.6.0/24 --dst-port 443 --ingress grafana-nci-staff-only
	openstack security group rule create --protocol tcp --ethertype IPv4 --remote-ip 130.56.245.149/32 --dst-port 3000 --ingress grafana-nci-staff-only
	openstack security group rule create --protocol tcp --ethertype IPv4 --remote-ip 150.203.248.0/24 --dst-port 3000 --ingress grafana-nci-staff-only

	openstack security group create ssh-nci-staff-only
	openstack security group rule create --protocol tcp --ethertype IPv4 --remote-ip 10.1.6.0/24 --dst-port 22 --ingress ssh-nci-staff-only
	openstack security group rule create --protocol tcp --ethertype IPv4 --remote-ip 150.203.248.0/24 --dst-port 22 --ingress ssh-nci-staff-only

	openstack security group create argocd-nci-staff-only
	openstack security group rule create --protocol tcp --ethertype IPv4 --remote-ip 10.1.6.0/24 --dst-port 8443 --ingress argocd-nci-staff-only
	openstack security group rule create --protocol tcp --ethertype IPv4 --remote-ip 130.56.245.34/32 --dst-port 8443 --ingress argocd-nci-staff-only
	openstack security group rule create --protocol tcp --ethertype IPv4 --remote-ip 130.56.245.149/32 --dst-port 8443 --ingress argocd-nci-staff-only
	openstack security group rule create --protocol tcp --ethertype IPv4 --remote-ip 10.1.9.0/24 --dst-port 8443 --ingress argocd-nci-staff-only
	openstack security group rule create --protocol tcp --ethertype IPv4 --remote-ip 150.203.248.0/24 --dst-port 8443 --ingress argocd-nci-staff-only

Update the inventory security groups to match the groups attached to each
node type. The Talos controller node is built separately, but its binding is
shown for completeness.

Ingress nodes have these security groups:

.. code-block:: yaml

	tl_os_security_groups:
	  - default
	  - http-nci-staff-only
	  - grafana-nci-staff-only
	  - argocd-nci-staff-only

Control-plane, worker, and elastic nodes use the default group:

.. code-block:: yaml

	tl_os_security_groups:
	  - default

The separately built Talos controller node uses:

.. code-block:: yaml

	vl_os_security_groups:
	  - default
	  - ssh-nci-staff-only

Optional External Monitoring
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a central Grafana service needs to monitor this environment, the initial
inventory example also uses an ``external-grafana`` security group to expose
Loki on TCP port 3100 and Prometheus on TCP port 9090. This group is optional
and is not part of the staff-facing rules listed above. Apply the source
network restrictions required by your environment, and add
``external-grafana`` to the ingress nodes' security groups only when this
monitoring access is required.

Object Storage
--------------

Gen3 uses S3-compatible object storage for data files, configurations, and
backups. Do not create any container with public access; public access allows
access without credentials.

Create the environment's containers, substituting its prefix as needed:

.. code-block:: console

	openstack container create gen3-train-backups
	openstack container create gen3-train-logs
	openstack container create gen3-train-upload
	openstack container create gen3-train-user-yaml

Server Group Anti-Affinity Rules
--------------------------------

Create one anti-affinity server group for each node type that should not share
an OpenStack compute node. Record each returned ID for the corresponding
``tl_os_scheduler_hints`` value in the inventory.

.. code-block:: console

	openstack server group create gen3-train-k8s-c3-cp --policy anti-affinity
	openstack server group create gen3-train-k8s-c3-es --policy anti-affinity
	openstack server group create gen3-train-k8s-c3-ingress --policy anti-affinity

SSL Certificates
----------------

Register the environment's DNS hostname in the Sectigo Certificate Portal and
add it to the ACME account before building. 

.. note::

    Sectigo is managed by ANU, and Kubernetes ``cert-manager`` uses the environment's ACME credentials to request
    certificates for service hostnames.

	Sectigo's enterprise validation uses a DNS record for the subdomain, so
	individual certificates do not require the DNS or HTTP validation commonly
	used by services such as Let's Encrypt. Once the hostname is registered,
	``cert-manager`` can request and renew its certificate using the ACME
	credentials stored in a Kubernetes secret. The issued certificate is stored
	in a Kubernetes TLS secret. Configure the service that terminates TLS to use
	that secret; no separate manual certificate request is needed for each
	service hostname covered by the registered subdomain.

    For example, Traefik can use a certificate secret as its default certificate.
    Traefik IngressRoutes can then use that default when serving their endpoints.
    Other TLS-terminating services can be configured to reference the appropriate
    certificate secret using their own configuration.

Create the Inventory
--------------------

Clone the `talos-k8s repository <https://git.nci.org.au/nci-vl/talos-k8s>`_,
create a branch for the environment, and create an inventory file based on an
existing inventory such as ``inventories/kf17-dev-talos-c1.yaml``. Update the
project, LDAP groups, security groups, IP addresses, floating IPs, bucket
names, server group IDs, and other environment-specific values.

The following inventory illustrates the configuration. Replace the example
values with the addresses and IDs created for your environment. The ingress
security group list follows the rules above.

.. code-block:: yaml

	# nd36 gen3-train environment inventory
	all:
	  vars:
	    tl_current_project: nd36
	    tl_os_network: nd36
	    tl_os_region: CloudV3
	    tl_os_auth_url: https://cloud.nci.org.au:5000
	    tl_cinder_csi_chart_version: "2.33.1"
	    ts_cinder_csi_app_cred_id: "{{ nd36_cinder_csi_app_cred_id }}"
	    ts_cinder_csi_app_cred_secret: "{{ nd36_cinder_csi_app_cred_secret }}"
	    tl_ingress_traefik_namespace: traefik
	    tl_ingress_traefik_chart_version: "39.0.0"
	    tl_ingress_traefik_ssl_hostname: "gen3-train.nci.org.au"
	    tl_ingress_traefik_endpoints:
	      - name: web
	        port: 80
	        redirect: websecure
	      - name: websecure
	        port: 443
	      - name: grafana3000
	        port: 3000
	      - name: argocd8443
	        port: 8443
	      - name: loki3100
	        port: 3100
	      - name: prometheus9090
	        port: 9090
	      # - name: openbao8200
	      #   port: 8200
	    tl_cert_manager_chart_version: "v1.18.2"
	    tl_ssl_ingress: true
	    tl_ssl_ingress_eab_kid: "{{ gen3_acme_eab_kid }}"
	    tl_ssl_ingress_eab_key: "{{ gen3_acme_eab_key }}"
	    tl_ssl_ingress_server: https://acme.sectigo.com/v2/OV
	    tl_k8s_dex_install: true
	    tl_k8s_cluster_name: gen3-train-tl-c1
	    tl_conf_dir: "/usr/local/talos"
	    oidc_hostname: "gen3-train.nci.org.au"
	    oidc_issuer_url: "https://{{ oidc_hostname }}/kube-auth"
	    oidc_client_id: "kubernetes"
	    oidc_username_claim: "preferred_username"
	    oidc_username_prefix: "ldap:"
	    oidc_groups_claim: "groups"
	    oidc_groups_prefix: "ldap:"
	    kube_auth_dex_issuer: "https://{{ oidc_hostname }}/kube-auth"
	    kube_auth_title: "Gen3 Train K8s"
	    kube_auth_oidc_client_id: "kubernetes"
	    tl_s3_endpoint: "https://cloud.nci.org.au:8080"
	    tl_s3_backup_bucket: "gen3-train-backups"
	    tl_snapshot_interval_minutes: "15"
	    tl_snapshot_versions: "96"
	    grafana_deploy: true
	    grafana_hostname: gen3-train.nci.org.au
	    grafana_editor_group: nd36
	    grafana_admin_group: cloud_admin
	    external_monitoring: true
	    tl_k8s_cluster_endpoint: 10.162.8.1
	    tl_k8s_jumpbox: nd36-train-talosctl
	    tl_workers_have_volumes: true
	    # tl_os_volume_type: "Nirin2_Transaction"
	    tl_app_environment: "gen3"
	  children:
	    jumpbox:
	      hosts:
	        nd36-train-talosctl:
	          tl_os_ip: 10.162.0.3
	          tl_os_floating_ip: 130.56.247.37
	          ansible_host: 130.56.247.37
	          ansible_user: "{{ tl_ssh_user }}"
	    cp_nodes:
	      vars:
	        tl_os_flavor: c3ep.4c8m20d
	        tl_os_security_groups:
	          - default
	        tl_os_image: "Talos Linux 1.13.9 2026-09-02"
	        tl_os_scheduler_hints: "group=3bc1f050-cfad-40bb-9c13-139122ef3a96"
	        tl_k8s_role: controlplane
	      hosts:
	        nd36-train-talos-c1-cp1:
	          tl_os_ip: 10.162.8.1
	        nd36-train-talos-c1-cp2:
	          tl_os_ip: 10.162.8.2
	        nd36-train-talos-c1-cp3:
	          tl_os_ip: 10.162.8.3
	    worker_nodes:
	      vars:
	        tl_os_flavor: c3ep.8c16m80d
	        tl_os_security_groups:
	          - default
	        tl_os_image: "Talos Linux 1.13.9 2026-09-02"
	        tl_os_scheduler_hints: "group=db5786e0-4ba1-48bc-822f-f996c28bc8c9"
	        tl_k8s_role: worker
	      hosts:
	        nd36-train-talos-c1-w1:
	          tl_os_ip: 10.162.8.10
	        nd36-train-talos-c1-w2:
	          tl_os_ip: 10.162.8.11
	        nd36-train-talos-c1-w3:
	          tl_os_ip: 10.162.8.12
	    elastic_nodes:
	      vars:
	        tl_os_flavor: c3ep.8c16m80d
	        tl_os_security_groups:
	          - default
	        tl_os_image: "Talos Linux 1.13.9 2026-09-02"
	        tl_os_scheduler_hints: "group=c98ca927-ded9-4501-98eb-9b33edb119e9"
	        tl_k8s_role: elastic
	      hosts:
	        nd36-train-talos-c1-es1:
	          tl_os_ip: 10.162.8.13
	        nd36-train-talos-c1-es2:
	          tl_os_ip: 10.162.8.14
	        nd36-train-talos-c1-es3:
	          tl_os_ip: 10.162.8.15
	    ingress_nodes:
	      vars:
	        tl_os_flavor: c3ep.4c8m20d
	        tl_os_security_groups:
	          - default
	          - http-nci-staff-only
	          - grafana-nci-staff-only
	          - argocd-nci-staff-only
	        tl_os_image: "Talos Linux 1.13.9 2026-09-02"
	        tl_os_scheduler_hints: "group=e543a8fd-91d6-4ab9-bfa5-ad9866051d64"
	        tl_k8s_role: ingress
	      hosts:
	        nd36-train-talos-c1-i1:
	          tl_os_ip: 10.162.8.7
	          tl_os_floating_ip: 130.56.244.70
	        nd36-train-talos-c1-i2:
	          tl_os_ip: 10.162.8.8
	          tl_os_floating_ip: 130.56.244.190

.. note::

	The inventory includes example server group IDs and addresses. Replace them
	with the IDs and IPs returned or assigned for your environment. If you enable
	external Grafana, Loki, or Prometheus access, use the applicable security
	group configuration for that environment.

Build the Cluster
-----------------

Source the OpenStack RC file for the environment, then run the cluster
playbook from the ``talos-k8s`` repository. Update the variables file, vault
file, and inventory path for the environment:

.. code-block:: console

	ansible-playbook --ask-pass --ask-become-pass --ask-vault-pass \
	  -e@~/ansible-common/nd36-train-k8s-vars.txt \
	  -e @~/ansible-vaults/gen3-train-k8s.vault \
	  -i inventories/nd36-train-talos-c1.yaml talos-cluster-gen3.yaml

Verify the Cluster
------------------

Log in to the jumpbox and complete the one-time Kubernetes authentication
setup:

.. code-block:: console

	/usr/local/bin/k8s-auth-setup

Open the displayed URL and log in to NCI LDAP. After authentication, verify
the cluster nodes:

.. code-block:: console

	kubectl get nodes

The command should report all control-plane, elastic, ingress, and worker
nodes as ``Ready``. For example:

.. code-block:: text

	NAME                     STATUS   ROLES           AGE   VERSION
	nd36-train-talos-c1-cp1   Ready    control-plane   43m   v1.36.3
	nd36-train-talos-c1-cp2   Ready    control-plane   43m   v1.36.3
	nd36-train-talos-c1-cp3   Ready    control-plane   43m   v1.36.3
	nd36-train-talos-c1-es1   Ready    <none>          43m   v1.36.3
	nd36-train-talos-c1-es2   Ready    <none>          43m   v1.36.3
	nd36-train-talos-c1-es3   Ready    <none>          43m   v1.36.3
	nd36-train-talos-c1-i1    Ready    <none>          43m   v1.36.3
	nd36-train-talos-c1-i2    Ready    <none>          43m   v1.36.3
	nd36-train-talos-c1-w1    Ready    <none>          43m   v1.36.3
	nd36-train-talos-c1-w2    Ready    <none>          43m   v1.36.3
	nd36-train-talos-c1-w3    Ready    <none>          43m   v1.36.3
