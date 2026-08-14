lint:
	uv run black potato/
	uv run mypy potato/

test:
	uv run pytest tests/
