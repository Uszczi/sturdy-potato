// Aspire TypeScript AppHost
// For more information, see: https://aspire.dev

import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

import { createBuilder } from "./.aspire/modules/aspire.mjs";

// `server` and `mcp` are uv workspace members, so uv keeps a single shared
// virtual environment at the repo root (../.venv), not a per-project one. Point
// the Python resources at it explicitly; otherwise Aspire defaults to
// `server/.venv`, a stale pre-workspace venv that lacks fastmcp/ollama and
// crashes the server on import.
const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const workspaceVenv = resolve(repoRoot, ".venv");

const builder = await createBuilder();

const postgres = await builder.addContainer("postgres", "postgres:17-alpine");
await postgres.withEnvironment("POSTGRES_USER", "postgres");
await postgres.withEnvironment("POSTGRES_PASSWORD", "postgres");
await postgres.withEnvironment("POSTGRES_DB", "sturdy_potato");
await postgres.withVolume("/var/lib/postgresql/data", {
  name: "sturdy-potato-postgres-data",
});
await postgres.withEndpoint({
  port: 5432,
  targetPort: 5432,
  scheme: "tcp",
  isProxied: false,
});

const redis = await builder.addContainer("redis", "redis:7-alpine");
await redis.withEndpoint({
  port: 6379,
  targetPort: 6379,
  scheme: "tcp",
  isProxied: false,
});

const DATABASE_URL =
  "postgresql+asyncpg://postgres:postgres@localhost:5432/sturdy_potato";

// Run Alembic migrations to head before the server starts. This runs to
// completion and exits (mirrors `just migrate`); the server waits for it below.
const migrations = await builder.addPythonExecutable("migrations", "../server", "alembic");
await migrations.withVirtualEnvironment(workspaceVenv);
await migrations.withUv();
await migrations.withArgs([
  "-c",
  "src/infrastructure/alembic/alembic.ini",
  "upgrade",
  "head",
]);
await migrations.withEnvironment("DATABASE_URL", DATABASE_URL);
await migrations.waitFor(postgres);

const server = await builder.addUvicornApp("server", "../server/src", "main:app");
await server.withVirtualEnvironment(workspaceVenv);
await server.withUv();
await server.withoutHttpsCertificate();
await server.withEnvironment("DATABASE_URL", DATABASE_URL);
await server.withEnvironment("REDIS_URL", "redis://localhost:6379/0");
await server.withHttpEndpoint({ port: 8000, targetPort: 8000, isProxied: false });
await server.withExternalHttpEndpoints();
await server.waitFor(postgres);
await server.waitFor(redis);
await server.waitForCompletion(migrations);

const client = await builder.addViteApp("client", "../client");
await client.withHttpEndpoint({ port: 5173, targetPort: 5173, isProxied: false });
await client.withReference(server);
await client.waitFor(server);
await client.withExternalHttpEndpoints();

await builder.build().run();
