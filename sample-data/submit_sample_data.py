#!/usr/bin/env python3
"""Submit synthetic records for the bundled training dictionary."""

import json
import os
from pathlib import Path

from gen3.auth import Gen3Auth
from gen3.submission import Gen3Submission

ENDPOINT = "http://gen3.kind.test"
PROGRAM = "training"
PROJECT = "demo"
RECORD_FILES = (
    "patient.json",
    "blood.json",
    "urine.json",
    "plasma.json",
    "dna.json",
)


def main() -> None:
    data_dir = Path(__file__).resolve().parent
    credentials_file = Path(
        os.environ.get(
            "GEN3_CREDENTIALS",
            str(Path.home() / "Downloads" / "gen3-credentials.json"),
        )
    ).expanduser()
    if not credentials_file.is_file():
        raise SystemExit(
            f"Credentials JSON not found: {credentials_file}. "
            "Set GEN3_CREDENTIALS to its path."
        )

    auth = Gen3Auth(endpoint=ENDPOINT, refresh_file=str(credentials_file))
    submission = Gen3Submission(auth)

    for filename in RECORD_FILES:
        records = json.loads((data_dir / filename).read_text(encoding="utf-8"))
        submission.submit_record(PROGRAM, PROJECT, records)
        print(f"Submitted {len(records)} records from {filename}.")


if __name__ == "__main__":
    main()
