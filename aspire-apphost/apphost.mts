// Aspire TypeScript AppHost
// For more information, see: https://aspire.dev

import { createBuilder } from "./.aspire/modules/aspire.mjs";

const builder = await createBuilder();

const django = await builder.addPythonApp("django", "..", "server/manage.py");
await django.withUv();
await django.withArgs(["runserver", "0.0.0.0:8001"]);
await django.withHttpEndpoint({ targetPort: 8001 });
await django.withExternalHttpEndpoints();

await builder.build().run();
