"""Definitions Dagster: ingest/extract à parte do job de warehouse."""

from __future__ import annotations

from dagster import AssetSelection, Definitions, define_asset_job
from dagster_dbt import DbtCliResource

from orchestration.assets_dbt import dbt_project, dbt_warehouse
from orchestration.assets_forecast import sarimax_cerveja
from orchestration.assets_lake import extract_assets, ingest_assets
from orchestration.paths import TRANSFORM_DIR, configure_dbt_paths

configure_dbt_paths()

ingest_sources = define_asset_job(
    name="ingest_sources",
    selection=AssetSelection.groups("ingest"),
)
extract_sources = define_asset_job(
    name="extract_sources",
    selection=AssetSelection.groups("extract"),
)
build_warehouse = define_asset_job(
    name="build_warehouse",
    selection=AssetSelection.assets(dbt_warehouse),
)
build_forecast = define_asset_job(
    name="build_forecast",
    selection=AssetSelection.assets(sarimax_cerveja),
)

defs = Definitions(
    assets=[*ingest_assets, *extract_assets, dbt_warehouse, sarimax_cerveja],
    jobs=[ingest_sources, extract_sources, build_warehouse, build_forecast],
    resources={
        "dbt": DbtCliResource(
            project_dir=dbt_project,
            profiles_dir=str(TRANSFORM_DIR),
        ),
    },
)
