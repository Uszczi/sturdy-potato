import { chromium } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import { dirname } from "node:path";

import { AUTH_FILE, DEMO_PASSWORD, DEMO_USER } from "./helpers";

// Logs in once as the demo user and stores the session that every spec reuses
// (see storageState in playwright.config.ts). Runs as a globalSetup instead of
// a setup *project* on purpose: globalSetup executes once before the tests in
// both `just e2e` and `just e2e-ui`, whereas a setup project is skipped in UI
// mode when its project is filtered out of the run — which left the specs
// reusing a stale session against the freshly-seeded server and every page
// returning DRF's 403 "Authentication credentials were not provided".
//
// The base URL is rebuilt from the same env vars as playwright.config.ts so the
// login hits the isolated e2e server booted by e2e/scripts/serve.sh.
async function globalSetup() {
  const host = process.env.E2E_HOST ?? "127.0.0.1";
  const port = process.env.E2E_PORT ?? "8099";
  const baseURL = `http://${host}:${port}`;

  await mkdir(dirname(AUTH_FILE), { recursive: true });

  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    await page.goto(`${baseURL}/accounts/login/?next=/`);

    await page.getByLabel("Username").fill(DEMO_USER);
    await page.getByLabel("Password").fill(DEMO_PASSWORD);
    await page.getByRole("button", { name: "Log in" }).click();

    // A successful login redirects to the overview page.
    await page.waitForURL(`${baseURL}/`);

    await page.context().storageState({ path: AUTH_FILE });
  } finally {
    await browser.close();
  }
}

export default globalSetup;
