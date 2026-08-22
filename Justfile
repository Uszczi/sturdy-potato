prod := "docker compose -f deployment/prod/docker-compose.yml"

all: lint test e2e

start:
	aspire start

db:
	docker run --rm --name sturdy-potato-postgres \
		-e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=sturdy_potato \
		-p 5432:5432 postgres:17-alpine

redis:
	docker run --rm --name sturdy-potato-redis -p 6379:6379 redis:7-alpine

run:
	cd server && \
	uv run fastapi dev src/main.py

# Serve the task tools over streamable HTTP at http://127.0.0.1:8001/mcp.
# Reuses the server's use cases in-process, so it needs the same running
# Postgres (and matching SECRET_KEY/DATABASE_URL) as the API.
mcp:
	cd mcp && \
	uv run potato-mcp

# Serve the task tools over stdio, so a client can launch the process directly.
# Credentials come from MCP_ACCESS_TOKEN and MCP_WORKSPACE_ID instead of headers.
mcp-stdio:
	cd mcp && \
	MCP_TRANSPORT=stdio uv run potato-mcp

# Chat with a local Ollama model that can call the task tools via the MCP server.
# Needs `just mcp` running, Ollama up (`docker compose up ollama`), and
# MCP_ACCESS_TOKEN / MCP_WORKSPACE_ID exported.
chat:
	cd mcp && \
	uv run potato-chat

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

create-admin password username="admin":
	cd server && \
	PYTHONPATH=src uv run python -m cli create-admin --username "{{username}}" --password "{{password}}"

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .pytest_cache -prune -exec rm -rf {} +
	find . -type d -name .mypy_cache -prune -exec rm -rf {} +
	find . -type d -name .ruff_cache -prune -exec rm -rf {} +
	rm -rf server/htmlcov server/.coverage

client-build:
	cd client && npm run build

client-lint:
	cd client && npm run lint

# Wipes the output dir first so files dropped from the spec don't linger, then
# formats the result. Needs the API up at http://localhost:8000 (`just run`).
# Regenerate the typed API client from the running server's OpenAPI schema.
generate-api-client:
	rm -rf ./client/api-client
	openapi-generator-cli generate -i http://localhost:8000/openapi.json -g typescript-fetch -o ./client/api-client --skip-validate-spec
	cd client && npx prettier --write "api-client/**/*.ts"

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
	uv run pytest --cov=src --cov-report=html:skip-covered --cov-fail-under=100 -v -n auto tests/

e2e-install:
	cd client && npx playwright install chromium

e2e *args:
	cd client && npx playwright test {{args}}

e2e-headed *args:
	cd client && npx playwright test --headed {{args}}

e2e-ui *args:
	cd client && npx playwright test --ui {{args}}

e2e-debug *args:
	cd client && npx playwright test --debug {{args}}

e2e-report:
	cd client && npx playwright show-report

prod-up:
	{{prod}} up --build

prod-down:
	{{prod}} down

prod-logs:
	{{prod}} logs -f web

prod-migrate:
	{{prod}} exec web alembic -c src/infrastructure/alembic/alembic.ini upgrade head

prod-seed:
	{{prod}} exec web python -m cli seed

prod-create-demo username="demo" password="demo-password-123":
	{{prod}} exec web python -m cli create-demo --username "{{username}}" --password "{{password}}"

prod-create-heavy username="heavy" password="heavy-password-123" projects="100" max_tasks="1000" completed_ratio="0.3" seed="0":
	{{prod}} exec web python -m cli create-heavy --username "{{username}}" --password "{{password}}" --projects "{{projects}}" --max-tasks "{{max_tasks}}" --completed-ratio "{{completed_ratio}}" --seed "{{seed}}"

prod-create-admin password username="admin":
	{{prod}} exec web python -m cli create-admin --username "{{username}}" --password "{{password}}"

prod-cli *args:
	{{prod}} exec web python -m cli {{args}}

prod-shell:
	{{prod}} exec web sh
