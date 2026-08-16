import { test, expect } from "@playwright/test";

test.describe("projects", () => {
  test("opens a seeded project from the projects list", async ({ page }) => {
    await page.goto("/projects/");

    await expect(
      page.getByRole("heading", { name: "Projects", exact: true }),
    ).toBeVisible();

    // Click the project in the main list (not the sidebar shortcut).
    await page
      .locator("#project-section")
      .getByRole("link", { name: /Getting started/ })
      .click();

    await expect(page).toHaveURL(/\/projects\/\d+\/$/);
    await expect(
      page.getByRole("heading", { name: "Getting started", exact: true }),
    ).toBeVisible();
  });
});
