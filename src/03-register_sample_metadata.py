#!/usr/bin/env python3
"""Register the uploaded synthetic FASTQ as a seqrun graph record."""

import argparse
import hashlib
from pathlib import Path

from gen3.auth import Gen3Auth
from gen3.index import Gen3Index
from gen3.submission import Gen3Submission

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = "http://gen3.kind.test"
CREDENTIALS_FILE = ROOT / "credentials.json"
SOURCE_FILE = ROOT / "sample-data" / "synthetic-demo.fastq"
PROGRAM = "training"
PROJECT = "demo"
UPLOAD_BUCKET = "gen3-local-upload"
DNA_SUBMITTER_ID = "SYN-DNA-001"
SEQ_RUN_SUBMITTER_ID = "SYN-SEQRUN-001"


def md5sum(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("guid", help="GUID printed by upload_sample_file.py")
    args = parser.parse_args()

    if not CREDENTIALS_FILE.is_file():
        raise SystemExit(f"Credentials file not found: {CREDENTIALS_FILE}")
    if not SOURCE_FILE.is_file():
        raise SystemExit(f"Sample file not found: {SOURCE_FILE}")

    record = {
        "type": "seqrun",
        "submitter_id": SEQ_RUN_SUBMITTER_ID,
        "seqrun_id": SEQ_RUN_SUBMITTER_ID,
        "object_id": args.guid,
        "file_name": SOURCE_FILE.name,
        "file_size": SOURCE_FILE.stat().st_size,
        "md5sum": md5sum(SOURCE_FILE),
        "state": "uploaded",
        "dnas": [{"submitter_id": DNA_SUBMITTER_ID}],
    }

    auth = Gen3Auth(endpoint=ENDPOINT, refresh_file=str(CREDENTIALS_FILE))
    index = Gen3Index(auth)
    index_record = index.get_record(args.guid)
    file_size = SOURCE_FILE.stat().st_size
    file_md5 = md5sum(SOURCE_FILE)
    storage_url = f"s3://{UPLOAD_BUCKET}/{args.guid}/{SOURCE_FILE.name}"

    existing_size = index_record.get("size")
    existing_md5 = (index_record.get("hashes") or {}).get("md5")
    if existing_size is not None and existing_size != file_size:
        raise SystemExit(
            f"GUID {args.guid} has size {existing_size}, but the local file is {file_size} bytes."
        )
    if existing_md5 and existing_md5 != file_md5:
        raise SystemExit(
            f"GUID {args.guid} has an MD5 that does not match the local FASTQ."
        )

    if existing_size is None or not existing_md5:
        index.update_blank(
            guid=args.guid,
            rev=index_record["rev"],
            hashes={"md5": file_md5},
            size=file_size,
            urls=[storage_url],
            authz=index_record.get("authz"),
        )
        print("Finalized the uploaded file's Indexd record.")
    elif storage_url not in (index_record.get("urls") or []):
        raise SystemExit(
            f"GUID {args.guid} is already finalized but does not point to the expected storage object."
        )

    submission = Gen3Submission(auth)
    submission.submit_record(PROGRAM, PROJECT, record)
    print(
        f"Submitted {SEQ_RUN_SUBMITTER_ID} to {PROGRAM}/{PROJECT}; "
        "run the search refresh before expecting it in Exploration."
    )


if __name__ == "__main__":
    main()
