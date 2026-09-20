.PHONY: sources test lint dvc-push dvc-pull ingest extract

sources:
	uv run betscerveja sources validate
	uv run betscerveja sources list

test:
	uv run pytest

lint:
	uv run ruff check src tests
	uv run ruff format --check src tests

ingest:
	uv run betscerveja ingest --source sidra_8885_pim_bebidas
	uv run betscerveja ingest --source bcb_sgs_rendimento_real

extract:
	uv run betscerveja extract --source sidra_8885_pim_bebidas
	uv run betscerveja extract --source sidra_8888_pim_geral
	uv run betscerveja extract --source sidra_7060_ipca
	uv run betscerveja extract --source bcb_sgs_rendimento_real

dvc-push:
	uv run python scripts/dvc_run.py push

dvc-pull:
	uv run python scripts/dvc_run.py pull
