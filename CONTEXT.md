# Sturdy Potato

A task tracker where people in a shared Workspace organise work into Projects and
move it across a Board. Each Project defines its own Workflow, so "the stages work
passes through" is a per-Project setting rather than a fixed pair of states.

## Language

### Ownership

**Workspace**:
The top-level container everyone and everything belongs to. A User joins one at
registration and may be a member of several.
_Avoid_: Team, organisation, account

**Project**:
A named grouping of Tasks inside a Workspace. Owns its own Workflow.
_Avoid_: List, board, category

**Task**:
A single unit of work. Belongs to a Workspace, optionally to a Project, and always
sits in exactly one Status.
_Avoid_: Todo, item, card, ticket

**Inbox**:
The Tasks in a Workspace that belong to no Project. It behaves as a Board in its
own right and uses the Workspace's Workflow.
_Avoid_: Unassigned, uncategorised, backlog

### Workflow

**Workflow**:
The ordered list of Statuses a Task may occupy. A Workspace owns a default
Workflow; each Project gets its own copy when it is created and edits it
independently thereafter.
_Avoid_: Status set, pipeline, states, board layout

**Status**:
One entry in a Workflow. Has a stable key that never changes, a label that can be
renamed freely, and its position in the Workflow's order.
_Avoid_: State, stage, phase

**Initial Status**:
The Status a newly created Task starts in. Every Workflow has exactly one.
_Avoid_: Default status, first status

**Terminal Status**:
A Status that means the work is finished. A Workflow has at least one and may have
several, so an ending like "Cancelled" can sit beside "Shipped".
_Avoid_: The Done Status, closed, final status

**Done**:
Of a Task: sitting in a Terminal Status. A property of the Task, never the name of
a particular Status — which is how it survives on a board whose endings are
"Shipped" and "Cancelled".
_Avoid_: Completed, finished, archived

**Open**:
Of a Task: not Done. This is what counts as outstanding work everywhere it is
totalled or listed.
_Avoid_: Active, incomplete, pending

### Board

**Board**:
The kanban view of one Project's Tasks (or of the Inbox), showing its Workflow as
side-by-side Columns.
_Avoid_: View, kanban, swimlane

**Column**:
The rendering of one Status on one Board, holding that Status's Tasks in their
manual order. A Column is always a Status *on a particular Board*: two Projects
that both have a "Review" Status have two separate Columns.
_Avoid_: Lane, bucket, stack
