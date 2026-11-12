#!/usr/bin/env python3
"""Upload the synthetic FASTQ payload to the local Gen3 commons."""

import hashlib
from pathlib import Path

import requests
from gen3.auth import Gen3Auth
from gen3.file import Gen3File

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = "http://gen3.kind.test"
CREDENTIALS_FILE = ROOT / "credentials.json"
SOURCE_FILE = ROOT / "sample-data" / "synthetic-demo.fastq"
AUTHZ_RESOURCE = "/programs/training/projects/demo"


def md5sum(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if not CREDENTIALS_FILE.is_file():
        raise SystemExit(f"Credentials file not found: {CREDENTIALS_FILE}")
    if not SOURCE_FILE.is_file():
        raise SystemExit(f"Sample file not found: {SOURCE_FILE}")

    auth = Gen3Auth(endpoint=ENDPOINT, refresh_file=str(CREDENTIALS_FILE))
    gen3_file = Gen3File(auth)

    try:
        upload_info = gen3_file.upload_file(
            file_name=SOURCE_FILE.name,
            authz=[AUTHZ_RESOURCE],
            protocol="s3",
        )
    except Exception as exc:
        raise SystemExit(
            f"Gen3 did not authorize the upload ({type(exc).__name__}). "
            "Check the credentials and upload permissions."
        ) from None

    if not isinstance(upload_info, dict):
        raise SystemExit("Gen3 returned an invalid upload response.")
    upload_url = upload_info.get("url")
    guid = upload_info.get("guid")
    if not upload_url or not guid:
        raise SystemExit("Gen3 upload response did not include a URL and GUID.")

    try:
        with SOURCE_FILE.open("rb") as source:
            response = requests.put(upload_url, data=source)
        response.raise_for_status()
    except requests.RequestException as exc:
        status = exc.response.status_code if exc.response is not None else "unavailable"
        raise SystemExit(
            f"Storage upload failed (HTTP status {status}). "
            "The presigned URL was not printed."
        ) from None

    print("Upload complete.")
    print(f"GUID: {guid}")
    print(f"File name: {SOURCE_FILE.name}")
    print(f"File size: {SOURCE_FILE.stat().st_size} bytes")
    print(f"MD5: {md5sum(SOURCE_FILE)}")
    print("Use these values when preparing the seqrun metadata record.")


if __name__ == "__main__":
    main()
