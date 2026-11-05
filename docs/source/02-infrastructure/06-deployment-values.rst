Gen3 Deployment Values
======================

This section outlines the files required for a Gen3 deployment. Argo CD uses
these values files to perform a Helm deployment of Gen3. The deployment uses
one or more values files containing the Helm configuration. The base global
values for Gen3 are described in the
`Gen3 Helm chart repository <https://github.com/uc-cdis/gen3-helm/tree/master/helm>`_.

There is a global values file for Gen3, along with more specific values files
for each Gen3 component. During a manual Helm install, configuration is
typically contained in one file. This deployment uses multiple files, which
are merged during an Argo CD deployment or sync.

Base Gen3 Values File
---------------------

The base values file is stored in the ``values`` directory for the environment
in the Gen3 Argo CD repository. For example:

.. code-block:: text

	 gen31k-train/values/gen31k-train-values.yaml

The inventory created earlier specifies the path to this file, for example:

.. code-block:: yaml

	 gen3_argo_values: "gen31k-train/gen3/values/gen31k-train-values.yaml"

Review the Gen3 documentation to understand the available configuration
parameters. Update the values file with the settings for your environment and
commit the changes.

Data Dictionary
---------------

Source or create a data dictionary for your Gen3 environment, then upload it to
the dictionary S3 bucket created earlier. You can use the OpenStack console or
AWS credentials with an S3 client such as ``s3cmd`` or ``awscli``.

For example, copy the file to the bucket with:

.. code-block:: console

	 s3cmd -c ~/.s3cfg.cloud.kf17_s3 put /tmp/1kg_V5noDir_bundled_schemaV2.json s3://gen3-dev-dictionary/1kg_V5noDir_bundled_schemaV2.json

.. note::

   ``~/.s3cfg.cloud.kf17_s3`` is an ``s3cmd`` configuration file in your home
   directory. It stores the S3 endpoint and credentials. It is created when
   ``s3cmd`` is configured (for example, with
   ``s3cmd --configure -c ~/.s3cfg.cloud.kf17_s3``), or it may be provided as
   part of environment setup.

   The config file is not necessarily specific to one bucket. The bucket and object
   key are specified separately in the ``s3://`` destination, and the same
   config can be used for multiple buckets if its credentials have access.
   Use a separate config when the endpoint or credentials differ. Ensure the
   selected credentials have permission to upload to the destination bucket.

Generate a presigned URL using the AWS credentials created during the
environment's OpenStack build stage. For example:

.. note::

	``presign-s3-url.py`` is an NCI-specific script that creates a time-limited
	URL for an S3 object. Creating the URL requires valid S3 credentials; the
	URL contains a signature generated using the secret key, so the recipient
	can retrieve the object without being given the credentials themselves.
	Anyone with the URL can access the object until the URL expires, so share it
	carefully.

.. code-block:: console

	 ./presign-s3-url.py --s3cfg ~/.s3cfg.cloud.nd36_s3 --object 1kg_V5noDir_bundled_schemaV2.json --bucket gen3-train-dictionary

Example output:

.. code-block:: text

	 Object https://cloud.nci.org.au:8080/1kg_V5noDir_bundled_schemaV2.json
	 URL:
	 "https://cloud.nci.org.au:8080/gen3-train-dictionary/1kg_V5noDir_bundled_schemaV2.json?AWSAccessKeyId=XXXXExpires=XXX&Signature=XXX"

In the base Gen3 values file, set ``dictionaryUrl`` to the presigned URL:

.. code-block:: yaml

	 global:
		 dictionaryUrl: "https://cloud.nci.org.au:8080/gen3-train-dictionary/1kg_V5noDir_bundled_schemaV2.json?AWSAccessKeyId=XXXXXXXXXXXXXXXXXXExpires=XXXXXXX&Signature=XXXXXXX"

Additional Component-Specific Configuration Files
--------------------------------------------------

The remaining values configuration is stored in files under the ``values.d``
directory in the environment-specific folder. These files are combined with
the base values file above to create the complete Gen3 ``values.yaml`` file.
Helm merges values under the same section into a single section.

Configure the following files with values specific to your Gen3 environment.
Their usage is described in the Gen3 documentation.

.. list-table:: Component-specific values files
	 :header-rows: 1
	 :widths: 32 68

	 * - File
		 - Usage
	 * - ``00-etl-mapping.yaml``
		 - Mappings used by the ETL process to generate the Elasticsearch indices.
	 * - ``01-usersync.yaml``
		 - Location of the user authorizations file and user-sync cron job
			 parameters. This file must specify the path to the ``user.yaml``
			 authorizations file in the ``userYamlS3Path`` field.
	 * - ``02-portal-gitops-css.yaml``
		 - CSS for the Gen3 data portal.
	 * - ``03-portal-gitops-json.yaml``
		 - Portal configuration, including text and values that must match the ETL
			 configuration and data dictionary.
	 * - ``04-fence.yaml``
		 - Fence configuration, primarily OIDC configuration.

Commit Changes
--------------

Commit the changes to the branch specified in the Gen3 inventory created
earlier.
