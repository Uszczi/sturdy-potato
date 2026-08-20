import { test, expect } from "@playwright/test";
import { DEMO_USER } from "./helpers";

// The register page redirects authenticated users away (beforeLoad in
// register.tsx), so this whole file runs logged out — overriding the shared
// authenticated session the config applies via storageState.
test.use({ storageState: { cookies: [], origins: [] } });

async function fillRegisterForm(
  page: import("@playwright/test").Page,
  { username, password, confirm }: { username: string; password: string; confirm: string },
) {
  await page.getByLabel("Username").fill(username);
  // "Password" would also match "Confirm password", so match it exactly.
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page.getByLabel("Confirm password").fill(confirm);
}

test.describe("register", () => {
  test("creates an account and lands signed in on the overview", async ({
    page,
  }) => {
    // Unique per run (and per retry) so it never collides with the seeded users
    // or a previous attempt against the same freshly-seeded database.
    const username = `newbie-${Date.now()}-${Math.floor(Math.random() * 1e6)}`;

    await page.goto("/register");
    await fillRegisterForm(page, {
      username,
      password: "a-good-password",
      confirm: "a-good-password",
    });
    await page.getByRole("button", { name: "Create account" }).click();

    // A successful registration signs the user in and redirects to the overview
    // (a protected page), which greets them by the name they registered with.
    await expect(page).toHaveURL(/\/$/);
    await expect(page.getByLabel("Workspace summary")).toBeVisible();
    await expect(page.getByText(username).first()).toBeVisible();
  });

  test("rejects a username that is already taken", async ({ page }) => {
    await page.goto("/register");
    await fillRegisterForm(page, {
      username: DEMO_USER,
      password: "a-good-password",
      confirm: "a-good-password",
    });
    await page.getByRole("button", { name: "Create account" }).click();

    await expect(page.getByRole("alert")).toContainText(
      "That username is already taken.",
    );
    await expect(page).toHaveURL(/\/register$/);
  });

  test("rejects mismatched passwords before calling the API", async ({
    page,
  }) => {
    await page.goto("/register");
    await fillRegisterForm(page, {
      username: `mismatch-${Date.now()}`,
      password: "a-good-password",
      confirm: "a-different-password",
    });
    await page.getByRole("button", { name: "Create account" }).click();

    await expect(page.getByRole("alert")).toContainText(
      "The passwords do not match.",
    );
    await expect(page).toHaveURL(/\/register$/);
  });
});
