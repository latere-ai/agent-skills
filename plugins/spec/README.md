# Spec workflow kit

The spec collection gives coding agents a durable workflow for design,
dependency planning, implementation, review, and completion. It stores the
working agreement in repository-owned Markdown so people and agents can inspect
the same source of truth.

Start with the [task-oriented usage guide](../../docs/spec-kit.md). This page is
the technical reference for installation, document structure, lifecycle rules,
and individual skills.

## Install

| Harness | Installation |
| --- | --- |
| Claude Code | `/plugin marketplace add latere-ai/agent-skills`, then `/plugin install spec@latere-ai` |
| Codex | Clone `latere-ai/agent-skills`, then run `python3 scripts/install.py codex spec` |

Claude Code exposes `/spec:<skill>`. Codex exposes the same workflow as
`$spec-<skill>`. Arguments and behavior are otherwise equivalent.

## Core contract

- Specs live under `specs/` and are reviewed with code.
- YAML frontmatter carries lifecycle state and dependency edges.
- The Markdown body carries intent, architecture, tests, and acceptance
  criteria.
- Skills read the host repository's instructions and commands before acting.
- Completion requires a testing verdict. A spec cannot jump directly from
  `validated` to `complete`.
- A task board is optional. The default workflow only needs files and Git.

## Document model

Every spec is a Markdown file under `specs/`. Grouping, ordering, and
dependencies are independent choices.

1. **Grouping:** a directory can name a track, such as
   `specs/local/live-serve.md`. A flat tree records `track:` in frontmatter.
2. **Ordering:** one directory may add an `NNN-` prefix for reading order. Each
   directory has its own number space.
3. **Dependencies:** `depends_on` contains repository-root-relative paths and
   forms one directed acyclic graph across the full tree.

`specs/local/003-live-serve.md` is both grouped and numbered. Its number does
not determine when it can be implemented; `depends_on` does.

```yaml
---
title: Live serve
status: validated
depends_on:
  - specs/shared/harness-abstraction.md
affects:
  - internal/server/
effort: medium
created: 2026-08-04
updated: 2026-08-04
author: someone
dispatched_task_id: null
---
```

When `specs/` does not exist, `create` bootstraps a flat tree and an index. It
does not impose track directories or numbering before the repository chooses
those conventions.

## Lifecycle

| State | Meaning |
| --- | --- |
| `vague` | The idea needs discovery before it can be reviewed |
| `drafted` | The design exists but has not passed validation |
| `validated` | Scope and dependencies are ready for implementation |
| `testing` | Implementation landed and awaits a drift verdict |
| `complete` | The delivered outcome was checked against the spec |
| `stale` | The document no longer matches current reality |
| `archived` | The work is intentionally retired |

The normal delivery path is `vague -> drafted -> validated -> testing ->
complete`. Changes in assumptions or implementation can move a live spec to
`stale`. `archived` specs can return to `drafted` when work resumes.

The complete transition map and diagram are in
[Using the spec kit](../../docs/spec-kit.md#the-lifecycle).

## Skill reference

| Purpose | Claude Code | Codex | Writes files? |
| --- | --- | --- | --- |
| Create and index a new design | `/spec:create` | `$spec-create` | Yes |
| Bring an outdated spec back to reality | `/spec:refine` | `$spec-refine` | Yes |
| Check fields, paths, states, and graph structure | `/spec:validate` | `$spec-validate` | No |
| Find code and spec blast radius | `/spec:impact` | `$spec-impact` | No |
| Split a design into child designs or tasks | `/spec:breakdown` | `$spec-breakdown` | Yes |
| Audit dependency order, size, gaps, and overlap | `/spec:review-breakdown` | `$spec-review-breakdown` | No |
| Record build intent or create linked board tasks | `/spec:dispatch` | `$spec-dispatch` | Yes |
| Implement a validated leaf with tests and docs | `/spec:implement` | `$spec-implement` | Yes |
| Judge implementation against acceptance criteria | `/spec:review-impl` | `$spec-review-impl` | No |
| Classify and record implementation divergence | `/spec:drift` | `$spec-drift` | Yes |
| Write the Outcome and finish legal transitions | `/spec:wrapup` | `$spec-wrapup` | Yes |
| Choose and run the next lifecycle step | `/spec:drive` | `$spec-drive` | Through other skills |
| Report status and actionable work | `/spec:report` | `$spec-report` | No |
| Repair one directory's numbering and index | `/spec:housekeeping` | `$spec-housekeeping` | Yes |

Use `drive` when you know the target spec but not the next command. Use `report`
when you need to understand the whole tree.

## Repository discovery

The implementation skills do not assume a programming language or build tool.
They discover working agreements from files such as `AGENTS.md`, `CLAUDE.md`,
`CONTRIBUTING.md`, `README.md`, package manifests, build files, and CI workflows.
They then use the host repository's test placement, formatting, build, and
documentation conventions.

If those conventions are missing or contradictory, the agent should report the
uncertainty instead of inventing a project rule. Clear repository instructions
make the workflow more reliable.

## Optional task-board integration

Most repositories use file-based dispatch. The skill records build intent in
the spec, commits the legal frontmatter transition, and leaves
`dispatched_task_id: null`.

Repositories may expose an HTTP transition API for atomic task creation,
dependency wiring, status changes, and drift handling. `dispatch` and `drive`
probe for that integration. If it is absent, they use the file-based path.

Task creation, cancellation, archival, broad stale propagation, and forced
completion are human gates. The orchestrator pauses before taking those
actions.

## Design limits

These skills structure agent work; they do not replace repository permissions,
CI, code review, or release ownership. The quality of an implementation still
depends on accurate local instructions, executable tests, and human judgment at
material gates.

## License

Licensed under the [MIT License](LICENSE).
