from dagster import AssetKey, Definitions
from orchestration.assets_dbt import dbt_warehouse
from orchestration.definitions import defs


def test_definitions_validate_loadable() -> None:
    Definitions.validate_loadable(defs)


def test_dbt_models_viram_assets_separados() -> None:
    assert len(dbt_warehouse.keys) > 1


def test_build_warehouse_nao_inclui_ingest() -> None:
    job = defs.resolve_job_def("build_warehouse")
    keys = set(job.asset_layer.executable_asset_keys)
    ingest = {key for key in keys if key.path[-1].startswith("ingest_")}
    extract = {key for key in keys if key.path[-1].startswith("extract_")}
    assert not ingest
    assert not extract
    assert AssetKey("ingest_sidra_8885_pim_bebidas") not in keys
