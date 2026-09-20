"""Demo local: sample commitado → dbt → SARIMAX → figuras → pacote Zenodo."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from betscerveja.figures.render import render_figures
from betscerveja.models.sarimax import duckdb_path, run_forecast
from betscerveja.registry import REPO_ROOT
from betscerveja.zenodo import pack_zenodo

SAMPLE_ROOT = REPO_ROOT / "data" / "sample"
SAMPLE_README = SAMPLE_ROOT / "README.md"

SAMPLE_EXTRACTS: tuple[str, ...] = (
    "cerveja/sidra_8885_pim_bebidas/extract.parquet",
    "cerveja/sidra_8888_pim_geral/extract.parquet",
    "macro/sidra_7060_ipca/extract.parquet",
    "macro/bcb_sgs_rendimento_real/extract.parquet",
    "cerveja/anuario_cerveja_ref2023_pub2024/extract.parquet",
    "cerveja/anuario_cerveja_ref2024_pub2025/extract.parquet",
    "cerveja/anuario_cerveja_ref2025_pub2026/extract.parquet",
)


def missing_sample_extracts(root: Path | str | None = None) -> list[str]:
    base = SAMPLE_ROOT if root is None else Path(root)
    return [rel for rel in SAMPLE_EXTRACTS if not (base / rel).is_file()]


def validate_sample(root: Path | str | None = None) -> Path:
    """Confere os sete Parquets. Não cai para `data/01_raw`."""
    base = SAMPLE_ROOT if root is None else Path(root)
    missing = missing_sample_extracts(base)
    if missing:
        listed = "\n".join(f"  - {rel}" for rel in missing)
        raise FileNotFoundError(
            "Faltam extracts em data/sample/ (o demo não usa data/01_raw):\n"
            f"{listed}\n"
            "Veja data/sample/README.md. Depois de `make dvc-pull` / extract, "
            "rode `uv run python scripts/sync_sample.py`."
        )
    return base


def run_demo() -> dict[str, str]:
    """dbt build no sample → forecast → figuras → Zenodo. Sem ingest, extract ou R2."""
    sample = validate_sample()
    _configure_duckdb()
    _run_dbt_build(sample)
    forecast = run_forecast()
    figures = render_figures()
    zenodo = pack_zenodo()
    figures_index = Path(figures["output_dir"]) / "index.html"
    return {
        "sample": str(sample),
        "duckdb": str(forecast["duckdb"]),
        "figures_index": str(figures_index),
        "zenodo_dir": str(zenodo["output_dir"]),
    }


def _configure_duckdb() -> Path:
    warehouse = REPO_ROOT / "warehouse"
    warehouse.mkdir(exist_ok=True)
    os.environ.setdefault(
        "BETSCERVEJA_DUCKDB_PATH",
        str((warehouse / "betscerveja.duckdb").resolve()),
    )
    return duckdb_path()


def _run_dbt_build(raw_root: Path) -> None:
    subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "export_dbt_seeds.py")],
        cwd=REPO_ROOT,
        check=True,
    )
    vars_payload = json.dumps({"raw_root": raw_root.resolve().as_posix()})
    subprocess.run(
        [
            _dbt_executable(),
            "build",
            "--project-dir",
            str(REPO_ROOT / "transform"),
            "--profiles-dir",
            str(REPO_ROOT / "transform"),
            "--vars",
            vars_payload,
        ],
        cwd=REPO_ROOT,
        check=True,
    )


def _dbt_executable() -> str:
    suffix = ".exe" if os.name == "nt" else ""
    candidate = Path(sys.executable).resolve().parent / f"dbt{suffix}"
    if candidate.is_file():
        return str(candidate)
    found = shutil.which("dbt")
    if found:
        return found
    raise FileNotFoundError("dbt não encontrado no ambiente. Rode `uv sync --extra dev`.")
