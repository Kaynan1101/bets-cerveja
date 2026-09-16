"""Ingestão idempotente: bytes imutáveis + manifest com sha256."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from betscerveja.registry import REPO_ROOT, Source

LANDING_ROOT = REPO_ROOT / "data" / "00_landing"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def manifest_path(source: Source) -> Path:
    return LANDING_ROOT / source.id / "_manifest.jsonl"


def known_hashes(source: Source) -> set[str]:
    path = manifest_path(source)
    if not path.exists():
        return set()
    hashes: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        hashes.add(json.loads(line)["sha256"])
    return hashes


def append_manifest(source: Source, record: dict) -> None:
    path = manifest_path(source)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_payload(source: Source, payload: bytes, suffix: str) -> tuple[Path, bool]:
    digest = sha256_bytes(payload)
    if digest in known_hashes(source):
        return LANDING_ROOT / source.id, True
    day = datetime.now(UTC).strftime("%Y-%m-%d")
    dest_dir = LANDING_ROOT / source.id / day
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"payload{suffix}"
    dest.write_bytes(payload)
    return dest, False
