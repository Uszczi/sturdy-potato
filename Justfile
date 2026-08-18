run:
	cd server && \
	uv run uvicorn main:app --reload

migrate:
	uv run alembic upgrade head

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

# The e2e suite lives with the React SPA it drives (client). Each
# recipe runs Playwright from there; it boots the SPA (Vite preview) and a
# freshly-seeded FastAPI server itself.

# Install the browsers Playwright needs to run the e2e suite.
e2e-install:
	cd client && npx playwright install chromium

# Run the Playwright e2e suite headless.
e2e *args:
	cd client && npx playwright test {{args}}

# Run the Playwright e2e suite in a visible browser window.
# Add `-- --slowmo 500` to slow the actions down enough to watch.
e2e-headed *args:
	cd client && npx playwright test --headed {{args}}

# Interactive UI mode: pick tests, watch them run, and time-travel through
# each step. The window stays open until you close it. Best for debugging.
e2e-ui *args:
	cd client && npx playwright test --ui {{args}}

# Step through a test with the Playwright Inspector (pauses on each action).
e2e-debug *args:
	cd client && npx playwright test --debug {{args}}

# Open the last Playwright HTML report.
e2e-report:
	cd client && npx playwright show-report

prod-up:
	docker compose -f deployment/prod/docker-compose.yml up --build

prod-down:
	docker compose -f deployment/prod/docker-compose.yml down

prod-logs:
	docker compose -f deployment/prod/docker-compose.yml logs -f web
