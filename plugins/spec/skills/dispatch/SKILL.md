---
name: dispatch
description: Check that a validated spec is ready to build and resolve its dependency wiring; where a task board with a transition API is present, create the linked task atomically. Also undispatches. Use when a design is settled and work should start — the spec must be validated and its dependencies complete.
argument-hint: <spec-file.md> [undispatch]
allowed-tools: Read, Grep, Glob, Edit, Agent, Bash(ls *), Bash(curl *)
---

# Dispatch a Spec

Check that a validated spec is ready to build, or undispatch a previously
dispatched spec. Where the repository runs a task board, dispatching also
creates the linked task; without one, dispatch changes no files.

## Step 0: Parse arguments

$ARGUMENTS has the form: `<spec-file.md> [undispatch]`

- The **first token** is the spec file path.
- If the second token is `undispatch`, perform an undispatch (cancel the linked
  task and clear `dispatched_task_id`).

## Step 1: Read the spec

1. Read the spec file in full. **Parse YAML frontmatter** — extract `title`,
   `status`, `depends_on`, `affects`, `effort`, `dispatched_task_id`.
2. Read the spec body to use as the task prompt.

## Step 2: Validate prerequisites

### For dispatch:

1. **Status check** — spec must be `validated`. If `drafted`, suggest
   `/spec:validate` first, then moving the status to `validated`. If `stale`,
   suggest `/spec:refine` first.
2. **Already dispatched check** — if `dispatched_task_id` is non-null, warn the
   user and stop. They must undispatch first or confirm re-dispatch.
3. **Dependency check** — for each path in `depends_on`, read that spec's
   frontmatter:
   - If the dependency has `status: complete`, it's satisfied.
   - If the dependency has `dispatched_task_id` set (task in progress), note it
     — the board task will block on the dependency's task via `DependsOn`.
   - If the dependency is neither complete nor dispatched, warn: the spec has
     unresolved dependencies. The user can proceed (the task will block) or
     resolve dependencies first.
4. **Leaf check** — determine if the spec is a leaf (no child directory with
   specs). Non-leaf specs can be dispatched, but warn the user: dispatching a
   parent spec means "implement this entire design as one task." If children
   exist, suggest dispatching the children individually instead.

### For undispatch:

1. **Has dispatch link** — `dispatched_task_id` must be non-null.
2. **Task status** — check the linked task's status. If it's `in_progress` or
   `committing`, warn: undispatching will cancel a running task.

## Step 3: Resolve dependencies

For dispatch to a task board, build the task's `DependsOn` list:

1. For each spec in `depends_on` that has a non-null `dispatched_task_id`, add
   that task UUID to `DependsOn`.
2. For dependencies that are `complete` (no active task), omit them from
   `DependsOn` — the work is already done.
3. For dependencies that are neither complete nor dispatched, omit them but
   flag a warning — the task won't have a dependency edge for these.

## Step 4: Execute

Dispatch has two implementations. Detect which applies before acting.

### Default: no task board

Most repos have no task board. Dispatch is then a readiness check that changes
no files: Step 2 already confirmed the spec is `validated`, and
`dispatched_task_id` stays `null` because there is no task to point at. Report
what would be built and in what order, so the user (or a following
`/spec:implement`) can pick it up.

### When a task board with a transition API is present

Some repos expose a server that owns dispatch atomically: it creates the board
task with a pre-assigned UUID,
resolves dependency edges, sets the spec `validated`, writes
`dispatched_task_id`, and commits the frontmatter in one transaction (a
folder/non-leaf path expands into its subtree leaves and promotes drafted
ancestors to `validated`). Detect it by probing the API; when it answers, use it
and do not hand-roll task creation or edit frontmatter yourself.

Dispatch:

```json
POST /api/specs/transition
{ "action": "dispatch", "paths": ["<workspace-relative spec path>"], "run": false }
```

- `paths` takes one or more specs (batch). `run: true` also moves the created
  task to `in_progress` immediately; default `false` leaves it queued.
- The response carries the created task UUID(s). The server has already written
  `dispatched_task_id` + `status: validated` and committed — you do not edit the
  file or commit.

Undispatch:

```json
POST /api/specs/transition
{ "action": "undispatch", "paths": ["<path>"] }
```

The server cancels the linked task if still active, clears
`dispatched_task_id`, resets `status` to `validated`, and commits.

If the transition endpoint fails but the task endpoints answer, fall back to
`POST /api/tasks/batch` with one `tasks` entry per spec: `prompt` = the spec
body, `spec_source_path` = the spec path (the server's task-done hook finds the
spec through it), `depends_on_refs` = the resolved task UUIDs (Step 3); then
edit the spec frontmatter (`dispatched_task_id`, `updated`) by hand and commit.
Flag clearly that this path loses the server's atomicity: a failed task create
can leave a dangling link.

## Step 5: Update spec file

Without a task board there is nothing to update.

With a transition API there is normally nothing to do — the server already wrote
and committed `dispatched_task_id`, `status`, and `updated`. Only on the
unreachable-server fallback do you edit the YAML frontmatter in place (changed
fields only), leaving the markdown body untouched.

## Step 6: Summary

Report to the user:
- What was dispatched/undispatched and the task UUID
- Dependency wiring: which task dependencies were resolved, which were skipped
- Any warnings (unresolved dependencies, non-leaf dispatch, running task cancel)
- Next steps: "Monitor on the task board", "Run `/spec:implement`", or
  "Dispatch dependencies first"

## Guidelines

- This skill is the bridge between designing and building. It should
  feel like a single action, not a multi-step process.
- Never assume a task board exists. Probe for it; the no-board path is the
  default, not the degraded mode.
- Where the transition API is present, prefer it over hand-rolling: it creates
  the task, sets `validated` + `dispatched_task_id`, and commits in one
  transaction.
- For batch dispatch through the API, pass multiple specs in one `paths` array
  so the server wires dependencies and creates tasks together.
- Commit only a frontmatter change you made yourself, on the task-endpoint
  fallback; do not push.
