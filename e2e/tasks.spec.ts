import { test, expect } from "@playwright/test";

test.describe("tasks", () => {
  test("creates a task and toggles it complete", async ({ page }) => {
    // Unique title keeps the test independent of any existing inbox contents.
    const title = `E2E task ${Date.now()}`;

    await page.goto("/tasks/");
    await expect(
      page.getByRole("heading", { name: "Inbox", exact: true }),
    ).toBeVisible();

    // Reveal the composer, then submit the new task (posted over HTMX).
    await page.getByRole("button", { name: "Add task" }).first().click();
    const titleInput = page.getByPlaceholder("What needs to be done?");
    await titleInput.fill(title);
    await page.locator("#task-composer button[type='submit']").click();

    const taskList = page.locator("#task-list");
    await expect(taskList.getByText(title, { exact: true })).toBeVisible();

    // The completion toggle for this task starts as "Mark ... as complete".
    // `exact` avoids matching the task row, whose accessible name aggregates
    // the labels of its child controls.
    const complete = page.getByRole("button", {
      name: `Mark ${title} as complete`,
      exact: true,
    });
    await expect(complete).toBeVisible();
    await complete.click();

    // After the HTMX swap the same task is now reopenable.
    await expect(
      page.getByRole("button", { name: `Mark ${title} as open`, exact: true }),
    ).toBeVisible();
  });
});
