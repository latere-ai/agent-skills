---
title: Open-source project guidance
status: testing
depends_on:
  - specs/harness-neutral-distribution.md
affects:
  - README.md
  - plugins/spec/README.md
  - plugins/spec/skills/
  - docs/
  - .github/
  - CONTRIBUTING.md
  - CODE_OF_CONDUCT.md
  - SECURITY.md
  - tests/
effort: medium
created: 2026-08-22
updated: 2026-08-22
author: changkun
dispatched_task_id: null
---

# Open-source project guidance

## Overview

Make `agent-skills` understandable and safe to adopt without prior knowledge of
Latere AI. First-time readers should quickly see what the project offers, how to
install it, when to use the spec kit, and how to contribute or report a problem.

## Current state

The root `README.md` documents installation but gives little help choosing or
using a workflow. `plugins/spec/README.md` describes the document model and
skill inventory, but it does not provide a task-oriented path from a real change
to a completed spec. The repository also lacks standard contributor, conduct,
security, issue, and pull-request guidance.

Several canonical skill instructions name fixed Go, Vue, Make, and Wallfacer
paths or commands. Those assumptions conflict with the repository's claim that
skills adapt to the project in which they run.

## Audience and surfaces

| Surface | Primary audience | First question answered |
| --- | --- | --- |
| `README.md` | Evaluator and new user | Why should I use this, and how do I start? |
| `docs/spec-kit.md` | Engineer adopting the workflow | Which skill do I run for my change? |
| `plugins/spec/README.md` | Technical user | What model and commands does this collection provide? |
| `CONTRIBUTING.md` | Contributor | How do I make a change that will be accepted? |
| `SECURITY.md` | Security reporter | How do I disclose a vulnerability safely? |
| GitHub templates | Issue or pull-request author | What evidence do maintainers need? |

## Components

### Public project entry point

Rewrite `README.md` around the user outcome, add build and license badges, give
each harness a copyable quick start, show the first useful command, state the
project's scope, and link deeper guidance.

### Spec kit guide

Add `docs/spec-kit.md` with prerequisites, a five-minute path, small and large
change workflows, lifecycle explanations, rendered workflow diagrams, command
mapping for both harnesses, team adoption guidance, optional task-board
behavior, and troubleshooting.

### Community health files

Add concise contribution, conduct, security, issue, and pull-request guidance.
Do not invent response times, support guarantees, or private contact addresses.

### Repository-agnostic skill behavior

Replace fixed project commands and paths in canonical skills with instructions
to discover and run the target repository's documented commands and conventions.
Keep concrete examples only when they are clearly labeled as examples.

## Testing strategy

- Validate that required open-source files and README badges exist.
- Check local Markdown links and fragments used by public documentation.
- Assert that canonical skills contain no fixed Wallfacer implementation paths
  or Go/Vue-only verification commands.
- Run the existing manifest and Codex installer suites.

## Acceptance criteria

- A new user can install the kit and reach a useful first command from the root
  README without reading skill source.
- The spec guide explains which workflow fits a small change, large change,
  stale spec, implementation review, and status check.
- Claude Code and Codex examples remain equivalent and copyable.
- README and lifecycle diagrams parse, render, and remain legible at normal
  documentation width.
- Public community health files give contributors actionable expectations.
- Skill instructions discover the host repository's commands instead of
  assuming Latere AI's former application stack.
- Documentation checks and the full existing test suite pass in CI.

## Outcome

### Summary

Implemented directly on 2026-08-22 in `47573f8` through `0940bdc`. All scoped
items shipped with minimal drift, and 17/17 automated tests pass.

### What shipped

- Reworked the root README around first-time user value, two copyable harness
  paths, verified CI and license badges, and a rendered workflow diagram.
- Added `docs/spec-kit.md` with a five-minute path, lifecycle visualization,
  small and large change workflows, all 14 skill mappings, team conventions,
  optional integration guidance, limits, and troubleshooting.
- Turned `plugins/spec/README.md` into a concise technical reference.
- Added contribution, conduct, security, issue, and pull-request guidance.
- Enabled GitHub private vulnerability reporting so the security policy's
  confidential disclosure path works.
- Removed fixed Go, Vue, Make, and private-service assumptions from canonical
  skills, and added first-use spec-tree bootstrapping.
- Added public-doc and portability regression tests to the existing installer
  and manifest coverage.

### Design evolution

- The requested visualization pass added two Mermaid diagrams after the initial
  spec was written. The spec and acceptance criteria now include them.
- The complete lifecycle remains authoritative in the state table. The diagram
  shows common delivery and recovery paths so it stays readable.

### Not implemented

- None.

### Unspecified work

- None beyond the user-requested visualization extension recorded above.

### Decisions, surprises, and follow-ups

- GitHub-native Mermaid was chosen because it renders in the repository without
  generated image assets or a documentation build pipeline.
- Visual verification caught an overly wide flow and a tangled complete-state
  graph. Both were simplified and rendered again before commit.
- The public guide separates evaluator, adopter, and technical-reference
  language instead of blending those audiences on one page.
- No support response times, security response times, or contact addresses were
  invented.
- Follow-ups: none.
