"""Run a DVC command with .env loaded and R2 checksum flags."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    load_dotenv(ROOT / ".env")
    os.environ.setdefault("AWS_REQUEST_CHECKSUM_CALCULATION", "when_required")
    os.environ.setdefault("AWS_RESPONSE_CHECKSUM_VALIDATION", "when_required")
    if len(sys.argv) < 2:
        raise SystemExit("usage: python scripts/dvc_run.py <dvc-args...>")
    raise SystemExit(subprocess.call(["dvc", *sys.argv[1:]], cwd=ROOT))


if __name__ == "__main__":
    main()
