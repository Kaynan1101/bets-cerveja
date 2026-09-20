"""Caminhos absolutos para o dbt rodar com cwd em transform/."""

from __future__ import annotations

import os

from betscerveja.registry import REPO_ROOT

TRANSFORM_DIR = REPO_ROOT / "transform"
WAREHOUSE_DIR = REPO_ROOT / "warehouse"
WAREHOUSE_PATH = WAREHOUSE_DIR / "betscerveja.duckdb"
RAW_ROOT = REPO_ROOT / "data" / "01_raw"


def configure_dbt_paths() -> None:
    WAREHOUSE_DIR.mkdir(exist_ok=True)
    os.environ["BETSCERVEJA_DUCKDB_PATH"] = str(WAREHOUSE_PATH.resolve())
