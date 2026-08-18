import { test, expect } from "@playwright/test";

test.describe("overview", () => {
  test("shows the workspace summary and seeded projects", async ({ page }) => {
    await page.goto("/");

    // The summary cards on the overview page (_app.index.tsx).
    const summary = page.getByLabel("Workspace summary");
    await expect(
      summary.getByText("Open tasks", { exact: true }),
    ).toBeVisible();
    await expect(summary.getByText("Completed", { exact: true })).toBeVisible();
    await expect(summary.getByText("Projects", { exact: true })).toBeVisible();

    // A seeded project appears once the store loads it from the API. The link
    // shows up in both the sidebar and the overview's projects panel.
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

    await expect(page).toHaveURL(/\/tasks$/);
    await expect(
      page.getByRole("heading", { name: "Inbox", exact: true }),
    ).toBeVisible();
  });
});
