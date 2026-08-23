import { test, expect, type Page } from "@playwright/test";

// Each project owns its own workflow — the ordered statuses its board renders as
// columns — so these tests work inside a freshly-created project. A new project
// copies the workspace default (Open / Done), and every edit here stays local to
// that project, which is what keeps parallel workers from colliding.

let seq = 0;
/** Collision-proof marker even when two workers share the same millisecond. */
function marker(): string {
  return `E2E workflow ${Date.now()}-${seq++}`;
}

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

async function addTask(page: Page, title: string): Promise<void> {
  await page.getByRole("button", { name: "Add task" }).first().click();
  await page.getByPlaceholder("What needs to be done?").fill(title);
  await page.locator("#task-composer button[type='submit']").click();
  await expect(
    page.locator("#task-list").getByText(title, { exact: true }),
  ).toBeVisible();
}

async function openKanbanForProject(page: Page, name: string): Promise<void> {
  await page.goto("/kanban");
  // The trigger is labelled with whichever project is already selected (the
  // choice is persisted), so open it positionally rather than by name.
  await page.locator(".dropdown > [role='button']").first().click();
  await page.locator(".dropdown-content").getByRole("button", { name }).click();
  await page.evaluate(() => (document.activeElement as HTMLElement)?.blur());
  await expect(
    page.locator(".dropdown-content").getByRole("button", { name }),
  ).toBeHidden();
  // The board fetches its cards and its columns together, so wait for the
  // columns to arrive before asserting anything about them.
  await expect(page.locator('[data-testid^="column-"]').first()).toBeVisible();
}

/** Open the workflow editor for the board currently on screen. */
async function openEditor(page: Page): Promise<void> {
  await page.getByRole("button", { name: "Edit columns" }).click();
  await expect(
    page.getByRole("heading", { name: /^Columns for/ }),
  ).toBeVisible();
}

async function save(page: Page): Promise<void> {
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: /^Columns for/ }),
  ).toBeHidden();
}

test.describe("board workflows", () => {
  test("a new project starts on the default two columns", async ({ page }) => {
    const project = marker();
    await createProjectAndOpen(page, project);
    await openKanbanForProject(page, project);

    await expect(page.getByTestId("column-open")).toBeVisible();
    await expect(page.getByTestId("column-done")).toBeVisible();
    await expect(page.locator('[data-testid^="column-"]')).toHaveCount(2);
  });

  test("adding a column renders it on the board", async ({ page }) => {
    const project = marker();
    await createProjectAndOpen(page, project);
    await openKanbanForProject(page, project);

    await openEditor(page);
    await page.getByRole("button", { name: "Add column" }).click();
    // The new column is appended, so its name input is the last one.
    await page.getByLabel("Column name").last().fill("In review");
    await save(page);

    await expect(page.locator('[data-testid^="column-"]')).toHaveCount(3);
    await expect(
      page.getByTestId("column-in-review").getByText("In review"),
    ).toBeVisible();
  });

  test("reordering columns changes the board's left-to-right order", async ({
    page,
  }) => {
    const project = marker();
    await createProjectAndOpen(page, project);
    await openKanbanForProject(page, project);

    await openEditor(page);
    // Send "Open" down so the board reads Done, Open.
    await page.getByRole("button", { name: "Move Open later" }).click();
    await save(page);

    const columns = page.locator('[data-testid^="column-"]');
    await expect(columns.nth(0)).toHaveAttribute("data-testid", "column-done");
    await expect(columns.nth(1)).toHaveAttribute("data-testid", "column-open");
  });

  test("renaming a column keeps its cards", async ({ page }) => {
    const project = marker();
    const taskTitle = `${marker()} card`;
    await createProjectAndOpen(page, project);
    await addTask(page, taskTitle);
    await openKanbanForProject(page, project);

    await openEditor(page);
    await page.getByLabel("Column name").first().fill("Backlog");
    await save(page);

    // The key never changes, so the card stays put under the new name.
    const column = page.getByTestId("column-open");
    await expect(column.getByText("Backlog")).toBeVisible();
    await expect(column.getByText(taskTitle, { exact: true })).toBeVisible();
  });

  test("removing a column moves its cards to the chosen one", async ({
    page,
  }) => {
    const project = marker();
    const taskTitle = `${marker()} card`;
    await createProjectAndOpen(page, project);
    await addTask(page, taskTitle);
    await openKanbanForProject(page, project);

    // Add a column to remove "Open" into. It has to take over as the starting
    // column too, since a board always needs exactly one.
    await openEditor(page);
    await page.getByRole("button", { name: "Add column" }).click();
    await page.getByLabel("Column name").last().fill("Backlog");
    await page.getByRole("radio").last().check();
    await save(page);

    await openEditor(page);
    await page.getByRole("button", { name: "Remove Open" }).click();
    await page
      .getByLabel("Move cards from Open to")
      .selectOption({ label: "Backlog" });
    await save(page);

    await expect(page.getByTestId("column-open")).toHaveCount(0);
    await expect(
      page.getByTestId("column-backlog").getByText(taskTitle, { exact: true }),
    ).toBeVisible();
  });

  test("removing a column demands somewhere for its cards to go", async ({
    page,
  }) => {
    const project = marker();
    await createProjectAndOpen(page, project);
    await openKanbanForProject(page, project);

    await openEditor(page);
    await page.getByRole("button", { name: "Add column" }).click();
    await page.getByLabel("Column name").last().fill("Backlog");
    await page.getByRole("radio").last().check();
    await save(page);

    await openEditor(page);
    await page.getByRole("button", { name: "Remove Open" }).click();
    await page.getByRole("button", { name: "Save", exact: true }).click();

    // The dialog stays open and says what is missing.
    await expect(page.getByRole("alert")).toContainText("should go");
    await expect(
      page.getByRole("heading", { name: /^Columns for/ }),
    ).toBeVisible();
  });

  test("removing the column that was chosen as a target clears it", async ({
    page,
  }) => {
    const project = marker();
    await createProjectAndOpen(page, project);
    await openKanbanForProject(page, project);

    // Four columns, so two can be removed and still leave the minimum two.
    await openEditor(page);
    await page.getByRole("button", { name: "Add column" }).click();
    await page.getByLabel("Column name").last().fill("Backlog");
    await page.getByRole("radio").last().check();
    await page.getByRole("button", { name: "Add column" }).click();
    await page.getByLabel("Column name").last().fill("Shipped");
    await page.getByRole("checkbox").last().check();
    await save(page);

    await openEditor(page);
    // Send Open's cards to Done, then remove Done as well. The first choice no
    // longer points anywhere, so it must not be sent to the server as-is.
    await page.getByRole("button", { name: "Remove Open" }).click();
    await page
      .getByLabel("Move cards from Open to")
      .selectOption({ label: "Done" });
    await page.getByRole("button", { name: "Remove Done" }).click();
    await page.getByRole("button", { name: "Save", exact: true }).click();

    // Named locally as a missing choice, not bounced back by the server.
    await expect(page.getByRole("alert")).toContainText("should go");
    await expect(page.getByLabel("Move cards from Open to")).toHaveValue("");
  });

  test("one project's columns don't touch another's", async ({ page }) => {
    const edited = marker();
    const untouched = marker();
    await createProjectAndOpen(page, edited);
    await createProjectAndOpen(page, untouched);

    await openKanbanForProject(page, edited);
    await openEditor(page);
    await page.getByRole("button", { name: "Add column" }).click();
    await page.getByLabel("Column name").last().fill("In review");
    await save(page);
    await expect(page.locator('[data-testid^="column-"]')).toHaveCount(3);

    await openKanbanForProject(page, untouched);
    await expect(page.locator('[data-testid^="column-"]')).toHaveCount(2);
  });
});
