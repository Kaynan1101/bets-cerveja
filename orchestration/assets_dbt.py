"""Cada model dbt vira um asset Dagster via dagster-dbt."""

from __future__ import annotations

import json
from pathlib import Path

from dagster_dbt import DbtCliResource, DbtProject, dbt_assets

from orchestration.paths import RAW_ROOT, TRANSFORM_DIR, configure_dbt_paths

configure_dbt_paths()

dbt_project = DbtProject(
    project_dir=TRANSFORM_DIR,
    profiles_dir=TRANSFORM_DIR,
)
dbt_project.prepare_if_dev()
if not Path(dbt_project.manifest_path).exists():
    dbt_project.preparer.prepare(dbt_project)


@dbt_assets(manifest=dbt_project.manifest_path, project=dbt_project)
def dbt_warehouse(context, dbt: DbtCliResource):
    raw_root = RAW_ROOT.resolve().as_posix()
    yield from dbt.cli(
        ["build", "--vars", json.dumps({"raw_root": raw_root})],
        context=context,
    ).stream()
