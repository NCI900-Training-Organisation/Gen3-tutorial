#!/usr/bin/env python3
"""Download a Gen3 file by GUID and verify it against its Indexd metadata."""

import argparse
import hashlib
from pathlib import Path

from gen3.auth import Gen3Auth
from gen3.file import Gen3File
from gen3.index import Gen3Index

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = "http://gen3.kind.test"
CREDENTIALS_FILE = ROOT / "credentials.json"
DEFAULT_GUID = "PREFIX/3ee620db-06c5-46c2-9bef-7e6729b8c8bd"
DEFAULT_OUTPUT_DIR = ROOT / "downloads"


def md5sum(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as downloaded:
        for chunk in iter(lambda: downloaded.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "guid",
        nargs="?",
        default=DEFAULT_GUID,
        help="Gen3 file GUID (defaults to the uploaded synthetic FASTQ)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="directory to save the downloaded file (default: %(default)s)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace a local file with the same name",
    )
    args = parser.parse_args()

    if not CREDENTIALS_FILE.is_file():
        raise SystemExit(f"Credentials file not found: {CREDENTIALS_FILE}")

    auth = Gen3Auth(endpoint=ENDPOINT, refresh_file=str(CREDENTIALS_FILE))
    index_record = Gen3Index(auth).get_record(args.guid)
    filename = index_record.get("file_name")
    if not filename or Path(filename).name != filename:
        raise SystemExit("Indexd did not return a safe file name for this GUID.")

    output_dir = args.output_dir.expanduser().resolve()
    destination = output_dir / filename
    if destination.exists() and not args.overwrite:
        raise SystemExit(
            f"File already exists: {destination}. "
            "Choose another --output-dir or pass --overwrite."
        )

    downloaded = Gen3File(auth).download_single(
        object_id=args.guid,
        path=str(output_dir),
    )
    if not downloaded or not destination.is_file():
        raise SystemExit("Gen3 did not complete the file download.")

    actual_size = destination.stat().st_size
    expected_size = index_record.get("size")
    if expected_size is not None and actual_size != expected_size:
        raise SystemExit(
            f"Downloaded size mismatch: expected {expected_size}, got {actual_size}."
        )

    actual_md5 = md5sum(destination)
    expected_md5 = (index_record.get("hashes") or {}).get("md5")
    if expected_md5 and actual_md5.lower() != expected_md5.lower():
        raise SystemExit("Downloaded MD5 does not match the Indexd record.")

    print(f"Downloaded: {destination}")
    print(f"GUID: {args.guid}")
    print(f"Size: {actual_size} bytes")
    print(f"MD5: {actual_md5}")


if __name__ == "__main__":
    main()
