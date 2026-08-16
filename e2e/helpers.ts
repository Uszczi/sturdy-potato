// Shared constants for the e2e suite. Credentials match the demo user created
// by `seeddb` and the defaults in e2e/scripts/serve.sh.

export const DEMO_USER = "demo";
export const DEMO_PASSWORD = process.env.SEEDDB_DEMO_PASSWORD ?? "demo-password-123";

// Where the authenticated session is persisted by e2e/global-setup.ts and
// reused by every test project (see storageState in playwright.config.ts).
//
// Kept OUTSIDE the e2e/ testDir on purpose: UI mode (`just e2e-ui`) watches
// testDir for changes, so writing the session file inside it would retrigger
// the setup test in an endless loop.
export const AUTH_FILE = "playwright/.auth/user.json";
