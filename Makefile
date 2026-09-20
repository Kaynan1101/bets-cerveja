.PHONY: sources test lint dvc-push dvc-pull ingest extract dbt-build sarimax figures ci dagster-dev

sources:
	uv run betscerveja sources validate
	uv run betscerveja sources list

test:
	uv run pytest

lint:
	uv run ruff check src tests orchestration
	uv run ruff format --check src tests orchestration

ingest:
	uv run betscerveja ingest --source sidra_8885_pim_bebidas
	uv run betscerveja ingest --source bcb_sgs_rendimento_real

extract:
	uv run betscerveja extract --source sidra_8885_pim_bebidas
	uv run betscerveja extract --source sidra_8888_pim_geral
	uv run betscerveja extract --source sidra_7060_ipca
	uv run betscerveja extract --source bcb_sgs_rendimento_real

dbt-build:
	uv run python scripts/export_dbt_seeds.py
	uv run python -c "from pathlib import Path; Path('warehouse').mkdir(exist_ok=True)"
	uv run dbt build --project-dir transform --profiles-dir transform

dvc-push:
	uv run python scripts/dvc_run.py push

dvc-pull:
	uv run python scripts/dvc_run.py pull

sarimax:
	uv run betscerveja forecast

figures:
	uv run betscerveja figures

ci: lint test dvc-pull dbt-build sarimax

dagster-dev:
	uv run dagster dev -m orchestration.definitions
