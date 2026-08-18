// Aspire TypeScript AppHost
// For more information, see: https://aspire.dev

import { createBuilder } from "./.aspire/modules/aspire.mjs";

const builder = await createBuilder();

const server = await builder.addUvicornApp("server", "../server/src", "main:app");
await server.withUv();
await server.withoutHttpsCertificate();
await server.withHttpEndpoint({ port: 8000, targetPort: 8000, isProxied: false });
await server.withExternalHttpEndpoints();

const client = await builder.addViteApp("client", "../client");
await client.withHttpEndpoint({ port: 5173, targetPort: 5173, isProxied: false });
await client.withReference(server);
await client.waitFor(server);
await client.withExternalHttpEndpoints();

await builder.build().run();
