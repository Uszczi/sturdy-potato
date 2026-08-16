import { defineConfig, devices } from "@playwright/test";

// Playwright drives the Django web app end-to-end. `just e2e` runs headless,
// `just e2e-headed` opens a real browser window. The webServer block boots an
// isolated, freshly-seeded Django instance (see e2e/scripts/serve.sh).

const HOST = process.env.E2E_HOST ?? "127.0.0.1";
const PORT = process.env.E2E_PORT ?? "8099";
const BASE_URL = `http://${HOST}:${PORT}`;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [["list"], ["html", { open: "never" }]],
  // Logs in once and writes the shared session before any spec runs. Used
  // instead of a setup project so the login also runs in UI mode, where a
  // setup project would be skipped when filtered out of the run.
  globalSetup: "./e2e/global-setup.ts",
  use: {
    baseURL: BASE_URL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        // Session written by globalSetup (e2e/global-setup.ts). Kept outside
        // testDir so UI mode's file watcher does not react to it (see
        // e2e/helpers.ts).
        storageState: "playwright/.auth/user.json",
      },
    },
  ],
  webServer: {
    command: "sh e2e/scripts/serve.sh",
    url: `${BASE_URL}/accounts/login/`,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    stdout: "pipe",
    stderr: "pipe",
    env: {
      E2E_HOST: HOST,
      E2E_PORT: PORT,
    },
  },
});
