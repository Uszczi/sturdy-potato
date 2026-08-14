lint:
	uv run black .
	uv run mypy .
	uv run ruff check . --fix

test:
	uv run pytest tests/
