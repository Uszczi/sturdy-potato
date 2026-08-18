run:
	cd server && \
	uv run uvicorn main:app --reload

migrate:
	uv run alembic -c ./server/infrastructure/alembic/alembic.ini upgrade head

makemigrations message:
	uv run alembic revision --autogenerate -m "{{message}}"

seed:
	cd server && \
	uv run python -m seed

generate-api-client:
	openapi-generator-cli generate -i http://localhost:8000/openapi.json -g typescript-fetch -o ./client/api-client

lint:
	uv run ruff check . --fix
	uv run ruff format .
	uv run mypy .

lint-check:
	uv run ruff check .
	uv run ruff format . --check
	uv run mypy .

test:
	uv run pytest --cov=server --cov-report=html:skip-covered --cov-fail-under=100 -v tests/

e2e-install:
	cd client && npx playwright install chromium

e2e *args:
	cd client && npx playwright test {{args}}

# Add `-- --slowmo 500` to slow the actions down enough to watch.
e2e-headed *args:
	cd client && npx playwright test --headed {{args}}

e2e-ui *args:
	cd client && npx playwright test --ui {{args}}

e2e-debug *args:
	cd client && npx playwright test --debug {{args}}

e2e-report:
	cd client && npx playwright show-report

prod-up:
	docker compose -f deployment/prod/docker-compose.yml up --build

prod-down:
	docker compose -f deployment/prod/docker-compose.yml down

prod-logs:
	docker compose -f deployment/prod/docker-compose.yml logs -f web
