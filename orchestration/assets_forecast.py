"""Asset fino do SARIMAX: mesma função do CLI, sem ingest de rede."""

from __future__ import annotations

from dagster import AssetKey, asset

from betscerveja.models.sarimax import run_forecast
from orchestration.assets_dbt import dbt_warehouse

ML_DATASET_DEPS = [
    key for key in dbt_warehouse.keys if key.path[-1] == "ml_dataset_cerveja_mensal"
] or [AssetKey("ml_dataset_cerveja_mensal")]


@asset(name="sarimax_cerveja", group_name="forecast", deps=ML_DATASET_DEPS)
def sarimax_cerveja() -> dict:
    return run_forecast()
