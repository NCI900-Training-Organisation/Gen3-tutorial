Gen3 User Authorization
=======================

Gen3 loads user authorization information from a YAML file. The file is
specific to your deployment and should reflect the Gen3 portal, data
dictionary, and the level at which you want to grant access.

Create the ``user.yaml`` file using the
`Fence user.yaml guide <https://github.com/uc-cdis/fence/blob/master/docs/additional_documentation/user.yaml_guide.md>`_.
Configure the deployment to read it from an S3 location. For example, the
base Gen3 configuration can specify:

.. code-block:: yaml

	gen3_user_yaml_s3: "s3://gen3-train-user-yaml/user.yaml"

Make sure the user-sync configuration in ``01-usersync.yaml`` points to the
same object through its ``userYamlS3Path`` setting.

Validate the file with the
`gen3users CLI <https://github.com/uc-cdis/gen3users#gen3users>`_ before
uploading or using it. This catches formatting and authorization-data issues
before they are ingested by Gen3.

Upload the File
---------------

Using the OpenStack console or an S3 client such as ``s3cmd``, upload
``user.yaml`` to the bucket and object path configured for user sync. For
example:

.. code-block:: console

	s3cmd put user.yaml s3://gen3-train-user-yaml/user.yaml

Gen3 deploys a cron job called ``usersync`` that ingests the file every five
minutes. After changing ``user.yaml``, you can also trigger the user-sync job
manually to apply the updates without waiting for the next scheduled run.
