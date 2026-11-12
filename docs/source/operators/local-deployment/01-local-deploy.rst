Deploy Gen3 Locally
===================

This guide deploys the repository's local Gen3 training environment: one Talos
control-plane node, local-path persistent storage, MinIO object storage, LDAP
and Dex login, HTTP ingress, and the Gen3 application. It is intended for a
disposable local training environment, not production.

Clone the repository first, then run repository commands from its root. All
Python tools in this tutorial use the existing ``~/.gen3-local-tools``
environment; activate it in each terminal session instead of creating another
environment for each tool. The deployment inputs include the bundled dictionary at
``sample-data-dict/output-json/bundled-schema.json``.

Platform support
----------------

The deployment playbooks in this repository currently support **macOS as the
deployment host**. ``01-build-infrastructure.yaml`` explicitly checks for
Darwin, starts Docker Desktop with ``open -a Docker``, and updates the macOS
DNS cache. The Debian instructions below install the required command-line
tools, but the current playbooks will stop before deployment on Debian. Do not
try to bypass those checks: the host networking and Docker Desktop assumptions
must first be ported and tested for Linux.

The cluster created by the playbook is pinned to Talos ``v1.14.5`` and
Kubernetes ``v1.37.1``. It allocates 6 CPUs and 8 GiB of memory to its single
control-plane node. Allow additional host memory and free disk space for Docker
and the Gen3 images, especially Elasticsearch and the ETL image.

Install prerequisites on macOS
---------------------------------

Install Homebrew if it is not already available. See the `Homebrew installation
guide <https://docs.brew.sh/Installation>`_ if the installer is not suitable
for your machine:

.. code-block:: console

	/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

Install Docker Desktop and the command-line tools used by the playbooks:

.. code-block:: console

	brew install --cask docker
	brew install siderolabs/tap/talosctl kubectl helm go python

Start Docker Desktop from Applications, accept its license, and wait until the
engine is ready. The playbook also attempts to open Docker Desktop for you.
Docker Desktop is subject to Docker's licensing terms; check those terms for
your organization.

Activate the existing Python environment, then install Ansible, its Kubernetes
client library, and the required collections into it:

.. code-block:: console

	source "$HOME/.gen3-local-tools/bin/activate"
	python -m pip install --upgrade pip
	python -m pip install ansible kubernetes==36.0.2 'boto3>=1.34' 'python-dateutil<3' PyYAML
	ansible-galaxy collection install kubernetes.core amazon.aws

Install the MinIO client (``mc``). MinIO Server itself is built and started as
a Docker container by the infrastructure playbook; do not install a second
host MinIO server for this setup.

.. code-block:: console

	mkdir -p "$HOME/.local/bin"
	GOBIN="$HOME/.local/bin" go install github.com/minio/mc@latest
	export PATH="$HOME/.local/bin:$PATH"

Make the ``PATH`` change persistent in your shell startup file if needed. The
playbooks look for ``mc`` in ``~/.local/bin``.

Start Docker Desktop and verify the tools:

.. code-block:: console

	open -a Docker
	docker info
	docker version
	talosctl version --client
	kubectl version --client
	helm version --short
	ansible-playbook --version
	mc --version
	openssl version

Use a ``talosctl`` client from the same Talos minor release as the cluster
(``v1.14.x`` for the supplied playbook). If you already have other Kubernetes
or Talos clusters configured, leave their contexts intact; the playbook
selects the local context by matching its Docker endpoint.

Install prerequisites on Debian
----------------------------------

These commands install Docker Engine and the local administration tools on
Debian 12 or 13. Docker access through the ``docker`` group is effectively
root-level access; only add a trusted account to that group. Log out and back
in after changing group membership.

Install Docker Engine from Docker's signed APT repository:

.. code-block:: console

	sudo apt-get update
	sudo apt-get install -y ca-certificates curl
	sudo install -m 0755 -d /etc/apt/keyrings
	sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
	sudo chmod a+r /etc/apt/keyrings/docker.asc
	sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null <<EOF
	Types: deb
	URIs: https://download.docker.com/linux/debian
	Suites: $(. /etc/os-release && echo "$VERSION_CODENAME")
	Components: stable
	Architectures: $(dpkg --print-architecture)
	Signed-By: /etc/apt/keyrings/docker.asc
	EOF
	sudo apt-get update
	sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
	sudo systemctl enable --now docker
	sudo docker run --rm hello-world

To run Docker without ``sudo``, add your account to the Docker group and start
a new login session:

.. code-block:: console

	sudo usermod -aG docker "$USER"

Install Python, Go, and other system utilities:

.. code-block:: console

	sudo apt-get install -y python3 python3-venv python3-pip golang-go openssl gpg

Install ``kubectl`` from the Kubernetes APT repository for the cluster's
``v1.37`` minor release:

.. code-block:: console

	sudo install -m 0755 -d /etc/apt/keyrings
	curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.37/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
	sudo chmod 644 /etc/apt/keyrings/kubernetes-apt-keyring.gpg
	echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.37/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
	sudo apt-get update
	sudo apt-get install -y kubectl

Install the matching Talos client. The release asset name uses the Debian
architecture reported by ``dpkg`` (normally ``amd64`` or ``arm64``):

.. code-block:: console

	TALOS_VERSION=v1.14.5
	ARCH=$(dpkg --print-architecture)
	curl -fL "https://github.com/siderolabs/talos/releases/download/${TALOS_VERSION}/talosctl-linux-${ARCH}" -o /tmp/talosctl
	sudo install -m 0755 /tmp/talosctl /usr/local/bin/talosctl
	rm /tmp/talosctl

Install Helm from its official binary releases. Choose a stable version
appropriate for the vendored chart, then verify its published checksum before
installing; see the `Helm installation and verification guide
<https://helm.sh/docs/intro/install/>`_.

Activate the existing Python environment, install Ansible dependencies and
collections into it, and install the MinIO client into the path expected by
the playbooks:

.. code-block:: console

	source "$HOME/.gen3-local-tools/bin/activate"
	python -m pip install --upgrade pip
	python -m pip install ansible kubernetes==36.0.2 'boto3>=1.34' 'python-dateutil<3' PyYAML
	ansible-galaxy collection install kubernetes.core amazon.aws
	mkdir -p "$HOME/.local/bin"
	GOBIN="$HOME/.local/bin" go install github.com/minio/mc@latest
	export PATH="$HOME/.local/bin:$PATH"

The current deployment playbooks are not supported on Debian, even after these
tools are installed. Use a macOS host for the steps below, or first port and
test the platform-specific assertions, Docker startup, DNS cache flush, and
host networking in the playbooks.

Check out the repository and inputs
--------------------------------------

From the repository root, activate the shared Python environment and confirm
the dictionary exists:

.. code-block:: console

	cd /path/to/Gen3-tutorial
	source "$HOME/.gen3-local-tools/bin/activate"



Build the local infrastructure
---------------------------------

On macOS, make sure Docker Desktop is running, then run:

.. code-block:: console

	ansible-playbook gen3-deployment/01-build-infrastructure.yaml --ask-become-pass

The become password is your macOS login password. It is requested for the
managed ``/etc/hosts`` entry; the playbook does not need it for every task.
This play creates or reuses the ``gen3-local`` Talos cluster, configures
single-node local-path storage, starts the pinned MinIO and LDAP containers,
creates the MinIO buckets and LDAP training user, and configures local DNS,
Traefik HTTP ingress, and Dex.

The playbook preserves existing cluster and service data. Do not delete Docker
volumes to work around an error: MinIO objects, PostgreSQL, Elasticsearch and
LDAP data are persistent.

Check that the node and local services are ready:

.. code-block:: console

	kubectl get nodes -o wide
	kubectl get pods -A
	docker ps --format 'table {{.Names}}\t{{.Status}}'
	curl -f http://minio.gen3.kind.test:9000/minio/health/live
	curl -f http://gen3.kind.test/dex/.well-known/openid-configuration

The hostname entries are managed in ``/etc/hosts`` by the infrastructure
playbook. If the play fails, read the first failed task and inspect its exact
resource before rerunning it.

Deploy the Gen3 application
------------------------------

After infrastructure checks pass, install the application:

.. code-block:: console

	ansible-playbook gen3-deployment/02-deploy-gen3.yaml

The application playbook installs PostgreSQL, Elasticsearch, Arborist, Fence,
Indexd, Sheepdog, Peregrine, Guppy, Portal and the reverse proxy. It uses the
dictionary bundled in the repository by default. To use a different bundled
schema, pass its absolute path with ``-e dictionary_file=/path/to/bundled-schema.json``;
review the ETL mappings before deploying a different schema.

Passwords and the Fence signing key are stored outside the repository in
``~/.gen3-local/`` with restrictive permissions. Back up this directory
securely. The playbook refuses to rotate database passwords or replace an
existing dictionary automatically.

Check deployments and persistent volumes:

.. code-block:: console

	kubectl get pods,pvc -n gen3
	kubectl get jobs -n gen3
	curl -f http://gen3.kind.test/user/_status

To open the Gen3 portal and log in:

#. Open a browser on the deployment host and go to
	`http://gen3.kind.test <http://gen3.kind.test>`_.
#. Select **Log In** (or **Login**) and choose **Training LDAP** as the
	identity provider.
#. Enter username ``mongoose`` and password ``mangoose``, then submit the
	login form. You should be redirected back to the Gen3 portal.


Refresh search after metadata changes
----------------------------------------

The first application deployment creates empty bootstrap indices so Guppy can
start before any training data has been submitted. On the first ETL run, force
the refresh because these bootstrap aliases do not have the timestamp expected
by incremental ETL:

.. code-block:: console

	ansible-playbook gen3-deployment/03-refresh-search.yaml -e etl_force=true

The ETL Job reads metadata and updates the versioned Elasticsearch indices and
aliases; it does not upload file contents. The playbook refuses to overlap an
active ETL Job, waits for completion, then restarts Guppy. If it reports an
active Job, check its state and do not start a second run:

.. code-block:: console

	kubectl get jobs -n gen3 -l gen3.training/task=etl
	kubectl get pods -n gen3 -l gen3.training/task=etl

After the first successful forced run, subsequent refreshes normally use the
incremental mode:

.. code-block:: console

	ansible-playbook gen3-deployment/03-refresh-search.yaml

Confirm the Guppy deployment is ready and verify that the submitted records
appear in Exploration.

Optional teardown
--------------------

Teardown is destructive. It removes the local Talos cluster and its Kubernetes
workloads, PostgreSQL and Elasticsearch data, MinIO files, LDAP users, and
local saved credentials. Back up anything needed first. To deliberately remove
this training environment on macOS:

.. code-block:: console

	ansible-playbook gen3-deployment/10-tear-down.yaml --ask-become-pass

The teardown playbook is scoped to the named ``gen3-local`` resources; review
its output before confirming any destructive action.
