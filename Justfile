lint:
	uv run black .
	uv run mypy .
	uv run ruff check . --fix
	uv run djlint . --reformat

lint-check:
	uv run black . --check
	uv run mypy .
	uv run ruff check .
	uv run djlint . --check

test:
	uv run pytest tests/
