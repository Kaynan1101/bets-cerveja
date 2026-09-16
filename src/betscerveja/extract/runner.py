"""Localiza o arquivo canônico no landing e extrai texto/tabelas para Parquet."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pdfplumber
import trafilatura

from betscerveja.ingest.manifest import LANDING_ROOT
from betscerveja.registry import REPO_ROOT, Source, TipoFonte
from betscerveja.schemas.raw import RawExtract

RAW_ROOT = REPO_ROOT / "data" / "01_raw"


def landing_file(source: Source) -> Path:
    folder = LANDING_ROOT / source.id
    if source.landing_filename:
        seed = folder / "seed" / source.landing_filename
        if seed.exists():
            return seed
    payload = sorted(folder.glob("*/payload.*"))
    if payload:
        return payload[-1]
    raise FileNotFoundError(f"nenhum arquivo em {folder}")


def extract_html(source: Source, path: Path) -> pd.DataFrame:
    html = path.read_text(encoding="utf-8", errors="replace")
    text = trafilatura.extract(html) or ""
    return pd.DataFrame(
        [
            {
                "source_id": source.id,
                "metodo": "trafilatura",
                "pagina": pd.NA,
                "trecho": text,
                "tabela_idx": pd.NA,
                "celulas_json": pd.NA,
            }
        ]
    )


def extract_pdf(source: Source, path: Path) -> pd.DataFrame:
    rows: list[dict] = []
    with pdfplumber.open(path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            rows.append(
                {
                    "source_id": source.id,
                    "metodo": "pdfplumber_text",
                    "pagina": page_number,
                    "trecho": text,
                    "tabela_idx": pd.NA,
                    "celulas_json": pd.NA,
                }
            )
            for table_idx, table in enumerate(page.extract_tables() or []):
                rows.append(
                    {
                        "source_id": source.id,
                        "metodo": "pdfplumber_table",
                        "pagina": page_number,
                        "trecho": pd.NA,
                        "tabela_idx": table_idx,
                        "celulas_json": json.dumps(table, ensure_ascii=False),
                    }
                )
    if not rows:
        raise ValueError(f"{source.id}: PDF sem texto nem tabela")
    return pd.DataFrame(rows)


def extract_source(source: Source) -> Path:
    src = landing_file(source)
    if source.tipo == TipoFonte.HTML:
        frame = extract_html(source, src)
    elif source.tipo == TipoFonte.PDF:
        frame = extract_pdf(source, src)
    else:
        raise ValueError(f"{source.id}: extração só para pdf/html")
    validated = RawExtract.validate(frame)
    dest_dir = RAW_ROOT / source.dominio / source.id
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "extract.parquet"
    validated.to_parquet(dest, index=False)
    return dest
