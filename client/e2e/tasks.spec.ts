import { test, expect, type Locator, type Page } from "@playwright/test";

/** Index of the first #task-list row containing `needle`, or -1. */
async function rowIndex(rows: Locator, needle: string): Promise<number> {
  const texts = await rows.allInnerTexts();
  return texts.findIndex((text) => text.includes(needle));
}

/** Create an inbox task via the composer and wait for its row. */
async function addTask(page: Page, title: string): Promise<void> {
  await page.getByRole("button", { name: "Add task" }).first().click();
  await page.getByPlaceholder("What needs to be done?").fill(title);
  await page.locator("#task-composer button[type='submit']").click();
  await expect(
    page.locator("#task-list").getByText(title, { exact: true }),
  ).toBeVisible();
}

test.describe("tasks", () => {
  test("creates a task and toggles it complete", async ({ page }) => {
    // Unique title keeps the test independent of the seeded inbox contents and
    // of other workers mutating the shared demo account in parallel.
    const title = `E2E task ${Date.now()}`;

    await page.goto("/tasks");
    await expect(
      page.getByRole("heading", { name: "Inbox", exact: true }),
    ).toBeVisible();

    // Reveal the composer, then submit the new task (posted to the API).
    await page.getByRole("button", { name: "Add task" }).first().click();
    await page.getByPlaceholder("What needs to be done?").fill(title);
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

    // After the store refreshes the same task is now reopenable.
    await expect(
      page.getByRole("button", { name: `Mark ${title} as open`, exact: true }),
    ).toBeVisible();
  });

  test("completing a task floats it to the top of the done group", async ({
    page,
  }) => {
    const marker = `E2E done-order ${Date.now()}`;
    const first = `${marker} A`;
    const second = `${marker} B`;

    await page.goto("/tasks");
    await expect(
      page.getByRole("heading", { name: "Inbox", exact: true }),
    ).toBeVisible();

    await addTask(page, first);
    await addTask(page, second);

    // Complete A, then B. B is ticked last, so it must land above A in the done
    // group even though A was created first (done is manually ordered now, and
    // completing floats the row to the top).
    for (const title of [first, second]) {
      await page
        .getByRole("button", { name: `Mark ${title} as complete`, exact: true })
        .click();
      await expect(
        page.getByRole("button", { name: `Mark ${title} as open`, exact: true }),
      ).toBeVisible();
    }

    const rows = page.locator("#task-list > li");
    await expect
      .poll(async () => rowIndex(rows, second))
      .toBeLessThan(await rowIndex(rows, first));

    // The order sticks across a reload (the client sent a column move).
    await page.reload();
    const reloaded = page.locator("#task-list > li");
    await expect(reloaded.getByText(second, { exact: true })).toBeVisible();
    expect(await rowIndex(reloaded, second)).toBeLessThan(
      await rowIndex(reloaded, first),
    );
  });
});
