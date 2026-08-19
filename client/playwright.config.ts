import { defineConfig, devices } from "@playwright/test";

// Playwright drives the React SPA end-to-end. `just e2e` runs headless,
// `just e2e-headed` opens a real browser window. Two servers are booted: the
// Vite dev server that serves the SPA (the app under test) and an isolated,
// freshly-seeded FastAPI instance that answers its API calls (see
// e2e/scripts/serve.sh).
//
// Ports deliberately differ from the app defaults (5173 / 8000) so the suite
// can run alongside a developer's dev servers without colliding — CI forbids
// reusing an existing server, so a stray dev server on the default ports would
// otherwise be silently tested instead.

// The SPA origin the browser loads.
const WEB_HOST = process.env.E2E_WEB_HOST ?? "127.0.0.1";
const WEB_PORT = process.env.E2E_WEB_PORT ?? "5273";
const BASE_URL = `http://${WEB_HOST}:${WEB_PORT}`;

// The FastAPI server. The browser talks to it same-origin: the Vite dev server
// proxies /api to this address (VITE_API_PROXY_TARGET below), so the SPA needs
// no hard-coded API host.
const API_HOST = process.env.E2E_API_HOST ?? "127.0.0.1";
const API_PORT = process.env.E2E_API_PORT ?? "8100";
const API_URL = `http://${API_HOST}:${API_PORT}`;

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
        // Session (JWT in localStorage) written by globalSetup
        // (e2e/global-setup.ts). Kept outside testDir so UI mode's file watcher
        // does not react to it (see e2e/helpers.ts).
        storageState: "playwright/.auth/user.json",
      },
    },
  ],
  webServer: [
    {
      // Isolated, freshly-seeded FastAPI API. serve.sh resolves the repo root
      // from its own location, so it runs from the default cwd (this config's
      // directory, client/).
      command: "sh e2e/scripts/serve.sh",
      // FastAPI always serves its schema once the app is up; used as readiness.
      url: `${API_URL}/openapi.json`,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      stdout: "pipe",
      stderr: "pipe",
      env: {
        E2E_API_HOST: API_HOST,
        E2E_API_PORT: API_PORT,
      },
    },
    {
      // Serve the SPA with the Vite dev server. It transpiles TS without a
      // type-check pass, so it does not depend on `tsc -b` / the production
      // build. Vite falls back to index.html for client-side routes, so deep
      // links like /tasks work. Swap this for `npm run build && npm run preview`
      // to exercise the production bundle once the tsc build is green.
      command: `npm run dev -- --host ${WEB_HOST} --port ${WEB_PORT} --strictPort`,
      url: BASE_URL,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      stdout: "pipe",
      stderr: "pipe",
      env: {
        // Point the dev server's /api proxy at the isolated e2e API port.
        VITE_API_PROXY_TARGET: API_URL,
      },
    },
  ],
});
