run:
	cd server && \
	uv run fastapi dev src/main.py

migrate:
	cd server && \
	uv run alembic -c src/infrastructure/alembic/alembic.ini upgrade head

makemigrations message:
	cd server && \
	uv run alembic -c src/infrastructure/alembic/alembic.ini revision --autogenerate -m "{{message}}"

seed:
	cd server && \
	uv run python src/seed.py

generate-api-client:
	openapi-generator-cli generate -i http://localhost:8000/openapi.json -g typescript-fetch -o ./client/api-client

lint:
	cd server && uv run ruff check . --fix
	cd server && uv run ruff format .
	cd server && uv run mypy .

lint-check:
	cd server && uv run ruff check .
	cd server && uv run ruff format . --check
	cd server && uv run mypy .

test:
	cd server && \
	uv run pytest --cov=src --cov-report=html:skip-covered --cov-fail-under=100 -v tests/

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
