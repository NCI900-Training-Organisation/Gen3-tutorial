#!/usr/bin/env python3
"""Create the local demo project under the existing training program."""

import argparse
from pathlib import Path

from gen3.auth import Gen3Auth
from gen3.submission import Gen3Submission

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = "http://gen3.kind.test"
CREDENTIALS_FILE = ROOT / "credentials.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--create-program",
        action="store_true",
        help="also create the training program; use only if it does not exist",
    )
    args = parser.parse_args()

    if not CREDENTIALS_FILE.is_file():
        raise SystemExit(f"Credentials file not found: {CREDENTIALS_FILE}")

    auth = Gen3Auth(endpoint=ENDPOINT, refresh_file=str(CREDENTIALS_FILE))
    submission = Gen3Submission(auth)

    if args.create_program:
        submission.create_program(
            {
                "type": "program",
                "name": "training",
                "dbgap_accession_number": "LOCAL-SYNTHETIC",
            }
        )
        print("Created program training.")

    submission.create_project(
        "training",
        {
            "code": "demo",
            "name": "Synthetic training project",
            "project_id": "training-demo",
            "dbgap_accession_number": "LOCAL-SYNTHETIC",
            "availability_type": "Open",
        },
    )
    print("Created project training/demo.")


if __name__ == "__main__":
    main()
