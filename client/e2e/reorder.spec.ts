import { test, expect, type Locator, type Page } from "@playwright/test";

// Exercises the drag-and-drop reordering wired up in TaskListView and the
// projects list. Tasks use their per-column move endpoint; projects retain
// their reorder endpoint. Each test reloads to prove the order persisted.

/** Index of the first row whose text contains `needle`, or -1. */
async function indexOf(rows: Locator, needle: string): Promise<number> {
  const texts = await rows.allInnerTexts();
  return texts.findIndex((text) => text.includes(needle));
}

/** Create a task through the composer and wait for its row to appear. */
async function addTask(page: Page, title: string): Promise<void> {
  await page.getByRole("button", { name: "Add task" }).first().click();
  await page.getByPlaceholder("What needs to be done?").fill(title);
  await page.locator("#task-composer button[type='submit']").click();
  await expect(
    page.locator("#task-list").getByText(title, { exact: true }),
  ).toBeVisible();
}

test.describe("reordering", () => {
  test("drags a task above another and persists the order", async ({
    page,
  }) => {
    // Unique, sortable marker so the two rows are found among the shared inbox.
    const marker = `E2E reorder ${Date.now()}`;
    const first = `${marker} A`;
    const second = `${marker} B`;

    await page.goto("/tasks");
    await expect(
      page.getByRole("heading", { name: "Inbox", exact: true }),
    ).toBeVisible();

    // New tasks append to the bottom, so B starts below A.
    await addTask(page, first);
    await addTask(page, second);

    const rows = page.locator("#task-list > li");
    expect(await indexOf(rows, second)).toBeGreaterThan(
      await indexOf(rows, first),
    );

    // Drag B onto A: B should take A's slot and end up above it.
    const rowA = rows.filter({ hasText: first });
    const rowB = rows.filter({ hasText: second });
    await rowB.dragTo(rowA);

    await expect
      .poll(async () => indexOf(rows, second))
      .toBeLessThan(await indexOf(rows, first));

    // Reload to confirm the API persisted the new order (not just local state).
    await page.reload();
    const reordered = page.locator("#task-list > li");
    await expect(reordered.getByText(second, { exact: true })).toBeVisible();
    expect(await indexOf(reordered, second)).toBeLessThan(
      await indexOf(reordered, first),
    );
  });

  test("drags a project above another and persists the order", async ({
    page,
  }) => {
    const marker = `E2E project ${Date.now()}`;
    const first = `${marker} A`;
    const second = `${marker} B`;

    await page.goto("/projects");
    await expect(
      page.getByRole("heading", { name: "Projects", exact: true }),
    ).toBeVisible();

    // Create two projects; the newest lands at the bottom of the list.
    for (const name of [first, second]) {
      await page.getByRole("button", { name: "Add project" }).first().click();
      await page.getByPlaceholder("What is this project about?").fill(name);
      await page.locator("#project-composer button[type='submit']").click();
      // The name renders twice per row (color-picker label + title), so match
      // the first occurrence.
      await expect(page.getByText(name, { exact: true }).first()).toBeVisible();
    }

    const rows = page.getByRole("list", { name: "Project list" }).locator("li");
    expect(await indexOf(rows, second)).toBeGreaterThan(
      await indexOf(rows, first),
    );

    await rows
      .filter({ hasText: second })
      .dragTo(rows.filter({ hasText: first }));

    await expect
      .poll(async () => indexOf(rows, second))
      .toBeLessThan(await indexOf(rows, first));

    await page.reload();
    const reordered = page
      .getByRole("list", { name: "Project list" })
      .locator("li");
    await expect(
      reordered.getByText(second, { exact: true }).first(),
    ).toBeVisible();
    expect(await indexOf(reordered, second)).toBeLessThan(
      await indexOf(reordered, first),
    );
  });
});
