import { test, expect } from "@playwright/test";

test.describe("overview", () => {
  test("shows the workspace summary and seeded projects", async ({ page }) => {
    await page.goto("/");

    await expect(
      page.getByRole("heading", { name: /Make room for the work/i }),
    ).toBeVisible();

    // The summary cards rendered by web/main.html.
    const summary = page.getByLabel("Workspace summary");
    await expect(summary.getByText("Open tasks", { exact: true })).toBeVisible();
    await expect(summary.getByText("Completed", { exact: true })).toBeVisible();

    // Seeded projects appear in the navigation and the projects panel.
    await expect(
      page.getByRole("link", { name: /Getting started/ }).first(),
    ).toBeVisible();
  });

  test("navigates from the sidebar to the inbox", async ({ page }) => {
    await page.goto("/");

    await page
      .getByRole("link", { name: "Inbox", exact: true })
      .first()
      .click();

    await expect(page).toHaveURL(/\/tasks\/$/);
    await expect(
      page.getByRole("heading", { name: "Inbox", exact: true }),
    ).toBeVisible();
  });
});
