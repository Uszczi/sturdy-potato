import { test, expect, type Locator, type Page } from "@playwright/test";

// Exercises the kanban board's drag-and-drop, which — unlike the native-HTML5
// drag used by the task/project lists — is driven by @dnd-kit/react's pointer
// sensor. So instead of Playwright's `dragTo` (which the pointer sensor ignores)
// these tests synthesise a real press / move / release gesture.
//
// Each test works inside its own freshly-created project so the board is
// isolated from the shared demo inbox and from other workers running in
// parallel: a brand-new project starts with both columns empty, which is what
// makes the "empty column" case reproducible.

let seq = 0;
/** Collision-proof marker even when two workers share the same millisecond. */
function marker(): string {
  return `E2E kanban ${Date.now()}-${seq++}`;
}

/** Create a project via the composer and open its detail page. */
async function createProjectAndOpen(page: Page, name: string): Promise<void> {
  await page.goto("/projects");
  await expect(
    page.getByRole("heading", { name: "Projects", exact: true }),
  ).toBeVisible();

  await page.getByRole("button", { name: "Add project" }).first().click();
  await page.getByPlaceholder("What is this project about?").fill(name);
  await page.locator("#project-composer button[type='submit']").click();

  const row = page
    .getByRole("list", { name: "Project list" })
    .locator("li")
    .filter({ hasText: name });
  await expect(row.first()).toBeVisible();

  await row.first().getByRole("link").first().click();
  await expect(page.getByRole("heading", { name, exact: true })).toBeVisible();
}

/** Add a task on the currently-open list (project detail or inbox). */
async function addTask(page: Page, title: string): Promise<void> {
  await page.getByRole("button", { name: "Add task" }).first().click();
  await page.getByPlaceholder("What needs to be done?").fill(title);
  await page.locator("#task-composer button[type='submit']").click();
  await expect(
    page.locator("#task-list").getByText(title, { exact: true }),
  ).toBeVisible();
}

/** Open the kanban and scope its board to the given project. */
async function openKanbanForProject(page: Page, name: string): Promise<void> {
  await page.goto("/kanban");
  await page.getByRole("button", { name: "Select project" }).click();
  await page
    .locator(".dropdown-content")
    .getByRole("button", { name })
    .click();
  // Close the dropdown — while it holds focus its content overlays the left
  // column and would swallow the pointerdown that starts a drag.
  await page.evaluate(() => (document.activeElement as HTMLElement)?.blur());
  await expect(
    page.locator(".dropdown-content").getByRole("button", { name }),
  ).toBeHidden();
  // The selector button now reflects the chosen project.
  await expect(page.getByRole("button", { name }).first()).toBeVisible();
}

/** A card locator matched by its (unique) title. */
function card(page: Page, title: string): Locator {
  return page.locator('[data-testid^="card-"]').filter({ hasText: title });
}

/** The card titles currently rendered in a column, top to bottom. */
async function columnOrder(page: Page, columnId: string): Promise<string[]> {
  // No drag in flight, so the floating overlay clone can't double a title.
  await expect(page.locator('[aria-grabbed="true"]')).toHaveCount(0);
  const texts = await page
    .getByTestId(columnId)
    // Skip dnd-kit's hidden drop placeholder, which briefly lingers as an
    // empty, aria-hidden card after a drop.
    .locator(
      '[data-testid^="card-"]:not([aria-hidden="true"]):not([data-dnd-placeholder])',
    )
    .allInnerTexts();
  return texts.map((text) => text.trim()).filter(Boolean);
}

/**
 * Press a card and drag it over `target`, running `whileHovering` (if given)
 * with the pointer still held down — used to assert the drop-target highlight
 * mid-drag. The pointer sensor needs an initial nudge to arm and stepped moves
 * so collision detection runs, otherwise the drop never registers.
 */
async function dragCardOnto(
  page: Page,
  source: Locator,
  target: Locator,
  whileHovering?: () => Promise<void>,
): Promise<void> {
  // A prior drop's overlay clone animates away on top of the board; wait it out
  // so this press lands on the card rather than the floating clone.
  await expect(page.locator('[aria-grabbed="true"]')).toHaveCount(0);
  // ...and let the prior drop's persist re-render settle: a remount mid-press
  // would cancel the new drag before it arms.
  await page.waitForTimeout(400);

  const s = await source.boundingBox();
  const t = await target.boundingBox();
  if (!s || !t) throw new Error("drag source/target has no bounding box");

  const sx = s.x + s.width / 2;
  const sy = s.y + s.height / 2;
  const tx = t.x + t.width / 2;
  const ty = t.y + t.height / 2;

  // Press and arm the pointer sensor, retrying the nudge if it didn't take —
  // under parallel CPU contention the first move can be dropped, leaving the
  // drag un-started (no floating clone) and the drop a no-op.
  for (let attempt = 0; ; attempt++) {
    await page.mouse.move(sx, sy);
    await page.mouse.down();
    await page.mouse.move(sx + 12, sy + 12, { steps: 5 }); // arm the sensor
    if ((await page.locator('[aria-grabbed="true"]').count()) > 0) break;
    await page.mouse.up();
    if (attempt >= 3) throw new Error("drag failed to arm");
    await page.waitForTimeout(150);
  }
  await page.mouse.move(tx, ty, { steps: 15 }); // travel to the column
  await page.mouse.move(tx, ty, { steps: 5 }); // settle so collision resolves
  // Let dnd-kit's onDragOver run before we assert the highlight / release.
  await page.waitForTimeout(150);

  if (whileHovering) await whileHovering();

  await page.mouse.up();
}

test.describe("kanban drag-and-drop", () => {
  test("moves a card into an empty column, highlighting it, and persists", async ({
    page,
  }) => {
    const project = marker();
    const taskTitle = `${project} task`;

    await createProjectAndOpen(page, project);
    await addTask(page, taskTitle);
    await openKanbanForProject(page, project);

    const openCol = page.getByTestId("column-open");
    const doneCol = page.getByTestId("column-done");

    // Baseline: the task sits in "open" and "done" is empty.
    await expect(openCol.getByText(taskTitle, { exact: true })).toBeVisible();
    await expect(doneCol.getByText(taskTitle)).toHaveCount(0);

    // Drag it onto the empty "done" column; that column should light up while
    // the pointer is over it.
    await dragCardOnto(page, card(page, taskTitle), doneCol, async () => {
      await expect(doneCol).toHaveAttribute("data-active", "true");
    });

    // The card now lives in "done", and "open" no longer holds it. `.first()`
    // tolerates dnd-kit's drag-overlay clone, which lingers for a beat after
    // the drop; the `toHaveCount(0)` below retries until it's gone.
    await expect(
      doneCol.getByText(taskTitle, { exact: true }).first(),
    ).toBeVisible();
    await expect(openCol.getByText(taskTitle)).toHaveCount(0);

    // Reload to prove the move round-tripped through the API (the selected
    // project is persisted, so the board comes back scoped to it).
    await page.reload();
    await expect(
      page
        .getByTestId("column-done")
        .getByText(taskTitle, { exact: true })
        .first(),
    ).toBeVisible();
    await expect(
      page.getByTestId("column-open").getByText(taskTitle),
    ).toHaveCount(0);
  });

  test("moves cards between populated columns and persists", async ({
    page,
  }) => {
    const project = marker();
    const first = `${project} A`;
    const second = `${project} B`;

    await createProjectAndOpen(page, project);
    await addTask(page, first);
    await addTask(page, second);
    await openKanbanForProject(page, project);

    const openCol = page.getByTestId("column-open");
    const doneCol = page.getByTestId("column-done");

    // Both start in "open".
    await expect(openCol.getByText(first, { exact: true })).toBeVisible();
    await expect(openCol.getByText(second, { exact: true })).toBeVisible();

    // A -> done (into an empty column), then B -> done (into a now-populated
    // column). "open" ends empty, "done" holds both. `.first()` tolerates the
    // transient drag-overlay clone left just after a drop.
    await dragCardOnto(page, card(page, first), doneCol);
    await expect(doneCol.getByText(first, { exact: true }).first()).toBeVisible();
    await expect(openCol.getByText(first)).toHaveCount(0);

    await dragCardOnto(page, card(page, second), doneCol);
    await expect(
      doneCol.getByText(second, { exact: true }).first(),
    ).toBeVisible();
    await expect(openCol.getByText(second)).toHaveCount(0);

    // Move A back to "open" — a populated -> other-column move in reverse.
    await dragCardOnto(page, card(page, first), openCol);
    await expect(openCol.getByText(first, { exact: true }).first()).toBeVisible();
    await expect(doneCol.getByText(first)).toHaveCount(0);

    // Final arrangement survives a reload: A open, B done.
    await page.reload();
    await expect(
      page.getByTestId("column-open").getByText(first, { exact: true }).first(),
    ).toBeVisible();
    await expect(
      page
        .getByTestId("column-done")
        .getByText(second, { exact: true })
        .first(),
    ).toBeVisible();
  });

  test("reorders cards within the done column and persists", async ({
    page,
  }) => {
    const project = marker();
    const titles = [`${project} A`, `${project} B`, `${project} C`];

    await createProjectAndOpen(page, project);
    for (const title of titles) await addTask(page, title);
    await openKanbanForProject(page, project);

    const doneCol = page.getByTestId("column-done");

    // Move all three into the done column (done is now manually orderable).
    for (const title of titles) {
      await dragCardOnto(page, card(page, title), doneCol);
      await expect(doneCol.getByText(title, { exact: true }).first()).toBeVisible();
    }
    await expect
      .poll(async () => (await columnOrder(page, "column-done")).length)
      .toBe(3);
    const before = await columnOrder(page, "column-done");

    // Drag the last done card onto the first: it should take the first slot.
    const last = before[before.length - 1];
    const first = before[0];
    await dragCardOnto(page, card(page, last), card(page, first));
    await expect.poll(async () => (await columnOrder(page, "column-done"))[0]).toBe(
      last,
    );

    // The manual order within done survives a reload — proof it persisted, not
    // just an optimistic reshuffle (done used to be recency-ordered).
    await page.reload();
    await expect(
      page.getByTestId("column-done").locator('[data-testid^="card-"]').first(),
    ).toBeVisible();
    expect((await columnOrder(page, "column-done"))[0]).toBe(last);
  });
});
