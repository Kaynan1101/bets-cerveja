"""Configure the DVC R2 remote from .env. Secrets go to .dvc/config.local."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


def _clean(value: str) -> str:
    return value.strip().strip("'").strip('"')


def main() -> None:
    load_dotenv(ROOT / ".env")
    url = _clean(os.environ["DVC_REMOTE_URL"])
    endpoint = _clean(os.environ["AWS_ENDPOINT_URL"]).rstrip("/")
    key = _clean(os.environ["AWS_ACCESS_KEY_ID"])
    secret = _clean(os.environ["AWS_SECRET_ACCESS_KEY"])
    if url.startswith("https://") and ".r2.cloudflarestorage.com/" in url:
        bucket = url.split(".r2.cloudflarestorage.com/", 1)[1].strip("/")
        url = f"s3://{bucket}"
    elif not url.startswith("s3://"):
        url = "s3://" + url.lstrip("/")

    def dvc(*args: str) -> None:
        subprocess.check_call(["uv", "run", "dvc", *args], cwd=ROOT)

    dvc("remote", "add", "-d", "r2", url)
    dvc("remote", "modify", "r2", "endpointurl", endpoint)
    dvc("remote", "modify", "r2", "region", "auto")
    dvc("remote", "modify", "--local", "r2", "access_key_id", key)
    dvc("remote", "modify", "--local", "r2", "secret_access_key", secret)
    bucket = url.removeprefix("s3://").split("/", 1)[0]
    print(f"DVC remote r2 configured for bucket {bucket} (secrets in .dvc/config.local)")


if __name__ == "__main__":
    main()
