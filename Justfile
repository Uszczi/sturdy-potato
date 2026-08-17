run:
	cd potato && \
	uv run python manage.py runserver

manage *args:
	cd potato && \
	uv run python manage.py {{args}}

makemigrations:
	cd potato && \
	uv run python manage.py makemigrations

migrate:
	cd potato && \
	uv run python manage.py migrate

seeddb:
	cd potato && \
	uv run python manage.py seeddb

generate-api-client:
	openapi-generator-cli generate -i http://localhost:8000/api/schema/ -g typescript-fetch -o ./web/sturdy-potato/api-client

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
	uv run pytest -n auto --cov=potato --cov-report=html:skip-covered --cov-fail-under=100 -v tests/

# Install the browsers Playwright needs to run the e2e suite.
e2e-install:
	npx playwright install chromium

# Run the Playwright e2e suite headless (boots its own seeded Django server).
e2e *args:
	npx playwright test {{args}}

# Run the Playwright e2e suite in a visible browser window.
# Add `-- --slowmo 500` to slow the actions down enough to watch.
e2e-headed *args:
	npx playwright test --headed {{args}}

# Interactive UI mode: pick tests, watch them run, and time-travel through
# each step. The window stays open until you close it. Best for debugging.
e2e-ui *args:
	npx playwright test --ui {{args}}

# Step through a test with the Playwright Inspector (pauses on each action).
e2e-debug *args:
	npx playwright test --debug {{args}}

# Open the last Playwright HTML report.
e2e-report:
	npx playwright show-report

prod-up:
	docker compose -f deployment/prod/docker-compose.yml up --build

prod-down:
	docker compose -f deployment/prod/docker-compose.yml down

prod-logs:
	docker compose -f deployment/prod/docker-compose.yml logs -f web

prod-manage *args:
	docker compose -f deployment/prod/docker-compose.yml run --rm web python manage.py {{args}}

