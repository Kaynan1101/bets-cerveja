.PHONY: sources test lint

sources:
	uv run betscerveja sources validate
	uv run betscerveja sources list

test:
	uv run pytest

lint:
	uv run ruff check src tests
	uv run ruff format --check src tests
