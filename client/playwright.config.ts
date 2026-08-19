import { defineConfig, devices } from "@playwright/test";

// Playwright drives the React SPA (web/sturdy-potato) end-to-end. `just e2e`
// runs headless, `just e2e-headed` opens a real browser window. Two servers are
// booted: the Vite preview server that serves the built SPA (the app under
// test) and an isolated, freshly-seeded Django instance that answers its API
// calls (see e2e/scripts/serve.sh).

// The SPA origin the browser loads. Must stay in Django's CORS allow-list
// (DJANGO_CORS_ALLOWED_ORIGINS defaults to 127.0.0.1:5173) so the JWT login and
// data calls to the API server are not blocked.
const WEB_HOST = process.env.E2E_WEB_HOST ?? "127.0.0.1";
const WEB_PORT = process.env.E2E_WEB_PORT ?? "5173";
const BASE_URL = `http://${WEB_HOST}:${WEB_PORT}`;

// The Django API server. src/api.ts hardcodes 127.0.0.1:8000, so the API must
// come up there for the SPA to reach it from the browser.
const API_HOST = process.env.E2E_API_HOST ?? "127.0.0.1";
const API_PORT = process.env.E2E_API_PORT ?? "8000";
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
    },
  ],
});
