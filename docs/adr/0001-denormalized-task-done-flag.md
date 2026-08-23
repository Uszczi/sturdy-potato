# Denormalised `is_done` flag on Task

Once each Project owns its own Workflow, whether a Task is finished depends on the
Project it belongs to: `status = "shipped"` may be Terminal in one Project and not
in another. That makes "is this Task Open?" unanswerable from the Task row alone,
yet three of our cheapest queries ask exactly that across a whole Workspace
(`list_open`, the `upcoming` view, and the open-count badge). We therefore store a
denormalised boolean `is_done` on the Task, indexed, and keep it in step on write.

## Considered Options

**Join against the owning Project's Workflow at query time.** Correct by
construction and impossible to desynchronise, but the Workflow is a JSON list on
the Project, so every Workspace-wide query becomes a `LEFT JOIN projects` with a
JSON containment check and a `COALESCE` to the Workspace's Workflow for Inbox
Tasks. Unindexable, and it makes our three most frequent reads the most expensive.

**Reserve a required `done` key in every Workflow.** Would keep the predicate a
plain column comparison, but it forbids more than one Terminal Status, which is
precisely what we wanted Workflows to allow.

## Consequences

`is_done` is derived data and can drift. Four write paths must maintain it: Task
creation, a Status change, a Project change (which re-maps the Status by
terminal-ness), and a Workflow edit that changes which Statuses are Terminal. The
last of these already walks the affected Project's Tasks in order to honour the
delete-a-Status-with-a-target rule, so it is not a new traversal.

`status` remains the source of truth. If the two ever disagree, `status` plus the
owning Workflow wins and `is_done` is the value to recompute.
