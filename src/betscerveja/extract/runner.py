"""Localiza o arquivo canônico no landing e extrai texto/tabelas/séries para Parquet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import pdfplumber
import trafilatura

from betscerveja.ingest.manifest import LANDING_ROOT
from betscerveja.registry import REPO_ROOT, Adapter, Source, TipoFonte
from betscerveja.schemas.raw import RawApiSeries, RawExtract

RAW_ROOT = REPO_ROOT / "data" / "01_raw"
SIDRA_MISSING = {"...", "..", "-", ""}


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


def _blank_to_na(value: Any) -> Any:
    if value is None:
        return pd.NA
    if isinstance(value, str) and value.strip() == "":
        return pd.NA
    return value


def _to_float(value: Any) -> Any:
    if value is None:
        return pd.NA
    if isinstance(value, str) and value.strip() in SIDRA_MISSING:
        return pd.NA
    try:
        return float(str(value).strip().replace(",", "."))
    except ValueError:
        return pd.NA


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _classificacao_fields(classificacoes: list[dict[str, Any]] | None) -> dict[str, Any]:
    if not classificacoes:
        return {
            "classificacao_id": pd.NA,
            "classificacao_nome": pd.NA,
            "categoria_id": pd.NA,
            "categoria_nome": pd.NA,
        }
    cls_ids: list[str] = []
    cls_nomes: list[str] = []
    cat_ids: list[str] = []
    cat_nomes: list[str] = []
    for item in classificacoes:
        cls_id = item.get("id")
        cls_nome = item.get("nome")
        if cls_id is not None:
            cls_ids.append(str(cls_id))
        if cls_nome:
            cls_nomes.append(str(cls_nome))
        categoria = item.get("categoria") or {}
        if isinstance(categoria, dict):
            for cat_id, cat_nome in categoria.items():
                cat_ids.append(str(cat_id))
                if cat_nome is not None:
                    cat_nomes.append(str(cat_nome))
    return {
        "classificacao_id": ";".join(cls_ids) or pd.NA,
        "classificacao_nome": ";".join(cls_nomes) or pd.NA,
        "categoria_id": ";".join(cat_ids) or pd.NA,
        "categoria_nome": ";".join(cat_nomes) or pd.NA,
    }


def extract_sidra(source: Source, path: Path) -> pd.DataFrame:
    payload = _load_json(path)
    if not isinstance(payload, list):
        raise ValueError(f"{source.id}: JSON SIDRA deve ser uma lista de variáveis")
    rows: list[dict] = []
    for variavel in payload:
        raw_variavel_id = variavel.get("id")
        variavel_id = (
            str(raw_variavel_id)
            if raw_variavel_id is not None and str(raw_variavel_id).strip() != ""
            else pd.NA
        )
        variavel_nome = _blank_to_na(variavel.get("variavel"))
        unidade = _blank_to_na(variavel.get("unidade"))
        for resultado in variavel.get("resultados") or []:
            classif = _classificacao_fields(resultado.get("classificacoes"))
            for serie in resultado.get("series") or []:
                localidade = serie.get("localidade") or {}
                valores = serie.get("serie") or {}
                if not isinstance(valores, dict):
                    continue
                for periodo, valor in valores.items():
                    rows.append(
                        {
                            "source_id": source.id,
                            "metodo": "api_sidra",
                            "periodo": str(periodo),
                            "localidade_id": _blank_to_na(localidade.get("id")),
                            "localidade_nome": _blank_to_na(localidade.get("nome")),
                            "variavel_id": variavel_id,
                            "variavel_nome": variavel_nome,
                            "unidade": unidade,
                            "valor": _to_float(valor),
                            **classif,
                        }
                    )
    if not rows:
        raise ValueError(f"{source.id}: SIDRA sem série")
    return pd.DataFrame(rows)


def extract_bcb(source: Source, path: Path) -> pd.DataFrame:
    payload = _load_json(path)
    if not isinstance(payload, list):
        raise ValueError(f"{source.id}: JSON SGS deve ser uma lista de pontos")
    rows: list[dict] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "source_id": source.id,
                "metodo": "api_bcb",
                "periodo": str(item.get("data", "")),
                "localidade_id": pd.NA,
                "localidade_nome": pd.NA,
                "variavel_id": pd.NA,
                "variavel_nome": pd.NA,
                "classificacao_id": pd.NA,
                "classificacao_nome": pd.NA,
                "categoria_id": pd.NA,
                "categoria_nome": pd.NA,
                "valor": _to_float(item.get("valor")),
                "unidade": pd.NA,
            }
        )
    if not rows:
        raise ValueError(f"{source.id}: SGS sem pontos")
    return pd.DataFrame(rows)


def _write_parquet(source: Source, frame: pd.DataFrame, schema: type) -> Path:
    validated = schema.validate(frame)
    dest_dir = RAW_ROOT / source.dominio / source.id
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "extract.parquet"
    validated.to_parquet(dest, index=False)
    return dest


def extract_source(source: Source) -> Path:
    src = landing_file(source)
    if source.tipo == TipoFonte.HTML:
        return _write_parquet(source, extract_html(source, src), RawExtract)
    if source.tipo == TipoFonte.PDF:
        return _write_parquet(source, extract_pdf(source, src), RawExtract)
    if source.tipo == TipoFonte.API:
        if source.adapter == Adapter.API_SIDRA:
            return _write_parquet(source, extract_sidra(source, src), RawApiSeries)
        if source.adapter == Adapter.API_BCB:
            return _write_parquet(source, extract_bcb(source, src), RawApiSeries)
        raise ValueError(f"{source.id}: adapter {source.adapter} sem extract de API")
    raise ValueError(f"{source.id}: extração só para pdf/html/api")
