run:
	cd potato && \
	uv run python manage.py runserver

makemigrations:
	cd potato && \
	uv run python manage.py makemigrations

migrate:
	cd potato && \
	uv run python manage.py migrate

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
	uv run pytest --cov=potato --cov-report=html:skip-covered tests/

prod-up:
	docker compose -f deployment/prod/docker-compose.yml up --build

prod-down:
	docker compose -f deployment/prod/docker-compose.yml down

prod-logs:
	docker compose -f deployment/prod/docker-compose.yml logs -f web

prod-manage *args:
	docker compose -f deployment/prod/docker-compose.yml run --rm web python manage.py {{args}}
