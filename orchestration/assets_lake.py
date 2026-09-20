"""Assets finos de ingest/extract — só as fontes que o dbt lê."""

from __future__ import annotations

from dagster import AssetKey, AssetsDefinition, asset

from betscerveja.extract.runner import extract_source
from betscerveja.ingest.runner import ingest_source
from betscerveja.registry import load_registry

WAREHOUSE_SOURCE_IDS = (
    "sidra_8885_pim_bebidas",
    "sidra_8888_pim_geral",
    "sidra_7060_ipca",
    "bcb_sgs_rendimento_real",
    "anuario_cerveja_ref2023_pub2024",
    "anuario_cerveja_ref2024_pub2025",
    "anuario_cerveja_ref2025_pub2026",
)


def _ingest_asset(source_id: str) -> AssetsDefinition:
    @asset(name=f"ingest_{source_id}", group_name="ingest")
    def _ingest() -> dict:
        return ingest_source(load_registry().get(source_id))

    return _ingest


def _extract_asset(source_id: str) -> AssetsDefinition:
    @asset(
        name=f"extract_{source_id}",
        group_name="extract",
        deps=[AssetKey(f"ingest_{source_id}")],
    )
    def _extract() -> str:
        return str(extract_source(load_registry().get(source_id)))

    return _extract


ingest_assets = [_ingest_asset(source_id) for source_id in WAREHOUSE_SOURCE_IDS]
extract_assets = [_extract_asset(source_id) for source_id in WAREHOUSE_SOURCE_IDS]
