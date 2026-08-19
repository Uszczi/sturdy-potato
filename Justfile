all: lint test e2e

start:
	aspire start

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
	PYTHONPATH=src uv run python -m cli seed

create-demo username="demo" password="demo-password-123":
	cd server && \
	PYTHONPATH=src uv run python -m cli create-demo --username "{{username}}" --password "{{password}}"

create-heavy username="heavy" password="heavy-password-123" projects="100" max_tasks="1000" completed_ratio="0.3" seed="0":
	cd server && \
	PYTHONPATH=src uv run python -m cli create-heavy --username "{{username}}" --password "{{password}}" --projects "{{projects}}" --max-tasks "{{max_tasks}}" --completed-ratio "{{completed_ratio}}" --seed "{{seed}}"

create-admin username="admin" password="admin-password-123":
	cd server && \
	PYTHONPATH=src uv run python -m cli create-admin --username "{{username}}" --password "{{password}}"

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .pytest_cache -prune -exec rm -rf {} +
	find . -type d -name .mypy_cache -prune -exec rm -rf {} +
	find . -type d -name .ruff_cache -prune -exec rm -rf {} +
	rm -rf server/htmlcov server/.coverage

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
