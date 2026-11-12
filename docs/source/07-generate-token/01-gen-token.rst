Generate an API Token and Download a File
========================================

Use the Gen3 Python SDK to exchange a downloaded API credential for a
short-lived access token, then download a file by its GUID. Install the SDK
into the shared ``~/.gen3-local-tools`` environment by following
:doc:`/08-gen3-sdk/01-install-sdk`. The SDK keeps the token in memory and
refreshes it when needed; do not print or commit it.

Create and download API credentials
-----------------------------------

#. Open the Gen3 portal at `http://gen3.kind.test <http://gen3.kind.test>`_.
#. Log in using **Training LDAP**.
#. Open **Profile** and create an API key.
#. In the confirmation dialog, select **Download JSON** and save the
   credentials file, for example as
   ``$HOME/Downloads/gen3-credentials.json``.

The credentials file contains a client ID and secret. Keep it private; do not
commit it to source control or paste it into chat or tickets.

Generate a token and download a file
------------------------------------

Save the following as ``download_gen3_file.py``. Replace ``YOUR-FILE-GUID``
with a GUID that your account is allowed to download:

.. code-block:: python

   from pathlib import Path

   from gen3.auth import Gen3Auth
   from gen3.file import Gen3File

   credentials_file = Path.home() / "Downloads" / "gen3-credentials.json"
   auth = Gen3Auth(refresh_file=str(credentials_file))

   # Obtain a short-lived access token without displaying or saving it.
   access_token = auth.get_access_token()
   if not access_token:
       raise RuntimeError("Gen3 did not return an access token")

   file_client = Gen3File(auth)
   downloaded = file_client.download_single(
       object_id="YOUR-FILE-GUID",
       path="downloads",
   )
   if not downloaded:
       raise RuntimeError("Gen3 file download failed")

Run the script from the activated environment:

.. code-block:: console

   python download_gen3_file.py

The SDK reads the API credential, obtains an access token from the local
commons, and uses that authenticated session to request the file. The file is
saved in the ``downloads`` directory. This local training deployment uses
HTTP; use it only on a trusted local machine or network.


