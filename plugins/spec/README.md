# spec

Spec-driven development for Claude Code. A design lives in a markdown file with
YAML frontmatter; the file carries a lifecycle state, a dependency edge list,
and the code paths it affects. The skills move specs through that lifecycle and
turn them into shipped code.

## Install

```
/plugin marketplace add latere-ai/claude-plugins
/plugin install spec@latere-ai
```

## The document model

Every spec is a markdown file under `specs/`, grouped into tracks — either
directories (`specs/<track>/name.md`) or a `track:` frontmatter field on flat
`specs/NNN-name.md` files. A spec with a same-named sibling directory is a
non-leaf: its children live inside.

```yaml
---
title: Live Serve
status: validated          # vague | drafted | validated | testing | complete | stale | archived
depends_on:                # paths to specs that must land first
  - specs/shared/harness-abstraction.md
affects:                   # code paths this spec touches
  - internal/server/
effort: medium             # small | medium | large | xlarge
created: 2026-08-04
updated: 2026-08-04
author: someone
dispatched_task_id: null
---
```

## The lifecycle

```
vague ──> drafted ──> validated ──> testing ──> complete
  │          │            │            │           │
  └──────────┴────────────┴────> stale ┘           │
             ▲                     │               │
             └─────────────────────┘               │
  archived <───────────────────────────────────────┘
  archived ──> drafted
```

`validated → complete` is deliberately not an edge. Completion runs through
`testing`, where the implementation is compared against what the spec asked for
and a verdict is rendered. That gate is what keeps a spec tree honest: a spec
reaches `complete` because someone checked, not because someone typed it.

## Skills

| Skill | What it does |
| --- | --- |
| `/spec:create` | Write a new design spec: gather context, explore the code, fill the frontmatter, index it |
| `/spec:refine` | Bring an out-of-date spec back in line with what the code actually does now |
| `/spec:validate` | Check the tree against the document model: fields, DAG acyclicity, orphans, dispatch consistency |
| `/spec:impact` | Blast radius of a proposed change, across both code and other specs |
| `/spec:breakdown` | Decompose a spec into child design specs or into implementation-ready leaves |
| `/spec:review-breakdown` | Audit a breakdown for dependency ordering, sizing, gaps, and boundary conflicts |
| `/spec:dispatch` | Mark a validated spec ready to build and wire its dependencies |
| `/spec:implement` | Build a spec: plan, implement each item with tests and docs, commit, finalize |
| `/spec:review-impl` | Check an implementation against the spec's acceptance criteria |
| `/spec:drift` | Classify how far what shipped diverged from the spec; record the verdict on it |
| `/spec:wrapup` | Close out a finished spec: Outcome section, status through the testing gate, index update |
| `/spec:drive` | Run the whole lifecycle toward a target state, stopping at gates. Start here when unsure |
| `/spec:report` | Survey the tree: what is done, in progress, blocked, and actionable |
| `/spec:housekeeping` | Tidy an out-of-order flat-numbered tree: stable ids, retire terminal specs, rebuild the index |

## Working without a server

The skills are file-first: a spec tree is markdown and git, and every skill
works with nothing else. Three skills — `dispatch`, `drive`, and `drift` — can
additionally drive a task board through an HTTP transition API when one is
present, which makes lifecycle changes atomic and adds automatic drift
detection on task completion. [Wallfacer](https://github.com/latere-ai/wallfacer)
is the reference implementation of that server. Absent it, the same transitions
happen as frontmatter edits along legal edges.

## License

MIT
