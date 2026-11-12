# Synthetic Gen3 sample data

These records are synthetic examples for the bundled dictionary. They contain
no real patient information. The files cover `patient`, `blood`, `urine`,
`plasma`, and `dna` and use the dictionary's required `type` and
`submitter_id` fields plus its declared links.

`synthetic-demo.fastq` is a tiny synthetic FASTQ payload for testing a file
upload. Its reads are artificial and are not biological data. Upload it with
`python src/upload_sample_file.py`; the uploader uses the repository-root
`credentials.json`. Only after upload should you create a `seqrun` record using
the returned GUID, actual file size, and calculated checksum. The metadata
submit script below does not upload file bytes or submit a `seqrun` record.

## Before submitting

Create the `training` program and `demo` project in the portal first, as
described in the local deployment guide. This matches the authorization path
configured for the local training user. The project code must be `demo`.

The dictionary's `program` node is not submittable through Sheepdog, so this
sample assumes the program and project already exist. The `seqrun` node is a
file node; it is intentionally omitted because it must reference a real
uploaded file GUID, filename, size, and checksum. Do not invent those fields.

## Submit with the Gen3 Python SDK

Install the SDK into the existing `~/.gen3-local-tools` environment using
`docs/source/08-gen3-sdk/01-install-sdk.rst`, then download an API credentials
JSON file from the portal Profile page. From the repository root, activate the
environment and run:

```sh
source "$HOME/.gen3-local-tools/bin/activate"
export GEN3_CREDENTIALS="$HOME/Downloads/gen3-credentials.json"
python sample-data/submit_sample_data.py
```

The script submits records in dependency order: patients, then blood and
urine, then plasma and DNA. It prints the number of submitted records, not the
access token. The API key must have permission to submit to `training/demo`.

The synthetic submitter IDs start with `SYN-`. Re-running the script submits
the same IDs again and may update those records; change the IDs before using a
second copy of this dataset.