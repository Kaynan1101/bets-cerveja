.PHONY: sources test lint dvc-push dvc-pull

sources:
	uv run betscerveja sources validate
	uv run betscerveja sources list

test:
	uv run pytest

lint:
	uv run ruff check src tests
	uv run ruff format --check src tests

dvc-push:
	uv run python scripts/dvc_run.py push

dvc-pull:
	uv run python scripts/dvc_run.py pull
