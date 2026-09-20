"""Copia os sete Parquets de data/01_raw → data/sample (depois de dvc pull / extract)."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from betscerveja.demo import SAMPLE_EXTRACTS, SAMPLE_ROOT
from betscerveja.registry import REPO_ROOT

RAW_ROOT = REPO_ROOT / "data" / "01_raw"


def sync_sample() -> list[Path]:
    missing = [rel for rel in SAMPLE_EXTRACTS if not (RAW_ROOT / rel).is_file()]
    if missing:
        listed = "\n".join(f"  - {rel}" for rel in missing)
        raise SystemExit(
            "Parquets de data/01_raw não encontrados. "
            "Rode `make dvc-pull` e, se ainda faltar, `make extract`. "
            "Não invente sample sintético.\n"
            f"{listed}"
        )
    copied: list[Path] = []
    for rel in SAMPLE_EXTRACTS:
        dest = SAMPLE_ROOT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(RAW_ROOT / rel, dest)
        copied.append(dest)
        print(f"copiou {rel}")
    return copied


if __name__ == "__main__":
    sync_sample()
    print(f"escreveu {len(SAMPLE_EXTRACTS)} extracts em {SAMPLE_ROOT}", file=sys.stderr)
