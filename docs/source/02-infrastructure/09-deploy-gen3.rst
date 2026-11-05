Deploying Gen3
==============

To deploy the Gen3 environment, run the Ansible playbook in the Gen3 deploy
repository.

This playbook will perform the tasks required for Gen3. It is mostly
idempotent, meaning it can be run repeatedly without causing major issues.

.. warning::

   One important thing to watch for is if there is already a populated Gen3
   database backup directory in the S3 backup bucket. In that case, creating the
   Gen3 DB cluster will appear to work, but backups and Write-Ahead Logs (WAL) will not be saved,
   and the cluster will eventually run out of space. Unless you know exactly
   what you are doing, you need to figure out what to do with any existing
   backups. You either need to delete the backup files, or move them aside if
   you want to restore from them later.

Before running the playbook, do one final check to ensure you are deploying to
the correct environment. Review the inventory file and confirm that the jumpbox
host is specified correctly:

.. code-block:: yaml

   children:
     jumpbox:
       hosts:
         nd36-train-talosctl

Run the playbook, passing it the vault, variable, and inventory file:

.. code-block:: console

   ansible-playbook --ask-vault-pass --ask-pass --ask-become-pass \
     -e @~/ansible-vaults/gen3-train-k8s.vault \
     -i inventory/nd36-test-gen3.yaml \
     build-gen3.yaml

.. note::

   The command does the following:

   * ``--ask-vault-pass`` prompts for the Ansible Vault password so the
     encrypted secrets file can be read.
   * ``--ask-pass`` prompts for the SSH password used to connect to the target
     hosts.
   * ``--ask-become-pass`` prompts for the sudo or become password required to
     run privileged tasks on the remote hosts.
   * ``-e @~/ansible-vaults/gen3-train-k8s.vault`` loads the encrypted
     environment variables and secrets from the vault file.
   * ``-i inventory/nd36-test-gen3.yaml`` points Ansible at the inventory for
     the correct environment.
   * ``build-gen3.yaml`` is the playbook that provisions and configures the
     Gen3 environment.

This will provision and configure the Gen3 environment using the settings for
that specific deployment.
