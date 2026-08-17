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

  test("morph swap preserves sibling task nodes across a toggle", async ({
    page,
  }) => {
    const stamp = Date.now();
    const toggled = `Morph toggled ${stamp}`;
    const sibling = `Morph sibling ${stamp}`;

    await page.goto("/tasks/");

    // Add both tasks through the HTMX composer.
    await page.getByRole("button", { name: "Add task" }).first().click();
    const titleInput = page.getByPlaceholder("What needs to be done?");
    const submit = page.locator("#task-composer button[type='submit']");
    for (const title of [sibling, toggled]) {
      await titleInput.fill(title);
      await submit.click();
      await expect(
        page.locator("#task-list").getByText(title, { exact: true }),
      ).toBeVisible();
    }

    // Brand the sibling's <li> with a JS-only expando property. It lives on the
    // DOM node itself, not in the server HTML, so it can only survive the toggle
    // if morph keeps that exact node instead of recreating it (as innerHTML
    // swapping would).
    const siblingRow = page.locator("#task-list > li", { hasText: sibling });
    await siblingRow.evaluate((el) => {
      (el as HTMLElement & { __morphKeep?: string }).__morphKeep = "kept";
    });

    // Toggle the *other* task. The response re-renders the whole list; morph
    // reconciles it in place.
    await page
      .getByRole("button", { name: `Mark ${toggled} as complete`, exact: true })
      .click();
    await expect(
      page.getByRole("button", {
        name: `Mark ${toggled} as open`,
        exact: true,
      }),
    ).toBeVisible();

    // The sibling node was never touched by the change, so morph left it — and
    // its expando — intact.
    await expect
      .poll(() =>
        siblingRow.evaluate(
          (el) =>
            (el as HTMLElement & { __morphKeep?: string }).__morphKeep ?? null,
        ),
      )
      .toBe("kept");
  });
});
