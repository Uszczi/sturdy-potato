// Aspire TypeScript AppHost
// For more information, see: https://aspire.dev

import { createBuilder } from "./.aspire/modules/aspire.mjs";

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

const server = await builder.addUvicornApp("server", "../server/src", "main:app");
await server.withUv();
await server.withoutHttpsCertificate();
await server.withEnvironment(
  "DATABASE_URL",
  "postgresql+asyncpg://postgres:postgres@localhost:5432/sturdy_potato",
);
await server.withEnvironment("REDIS_URL", "redis://localhost:6379/0");
await server.withHttpEndpoint({ port: 8000, targetPort: 8000, isProxied: false });
await server.withExternalHttpEndpoints();
await server.waitFor(postgres);
await server.waitFor(redis);

const client = await builder.addViteApp("client", "../client");
await client.withHttpEndpoint({ port: 5173, targetPort: 5173, isProxied: false });
await client.withReference(server);
await client.waitFor(server);
await client.withExternalHttpEndpoints();

await builder.build().run();
