---
title: Harness-neutral skill distribution
status: drafted
depends_on: []
affects:
  - README.md
  - plugins/spec/README.md
  - plugins/spec/.claude-plugin/plugin.json
  - .claude-plugin/marketplace.json
  - scripts/
  - tests/
effort: medium
created: 2026-08-22
updated: 2026-08-22
author: changkun
dispatched_task_id: null
---

# Harness-neutral skill distribution

## Overview

Rename the repository from `claude-plugins` to `agent-skills` and make the
skills installable in Codex without removing the existing Claude Code
marketplace. The skill sources remain shared so fixes cannot drift between
harness-specific copies.

## Current state

The canonical skills live under `plugins/spec/skills/`. Claude Code discovers
them through `.claude-plugin/marketplace.json` and
`plugins/spec/.claude-plugin/plugin.json`. Documentation, metadata, and
`scripts/validate.py` currently describe only Claude Code, and Codex has no
supported installation path from this repository.

## Architecture

Claude Code continues to consume the source tree through its marketplace
adapter. A local Python installer copies the same source skills into Codex's
skills directory and performs the minimal harness adaptation at install time:
skill names become `spec-<name>`, `/spec:<name>` references become
`$spec-<name>`, and Claude-only frontmatter fields are omitted.

The repository is renamed to `latere-ai/agent-skills`; manifests and user docs
must use the canonical new URL. The old GitHub URL may redirect, but it is not
part of the documented contract.

## Components

### Codex installer

Add `scripts/install.py` with a `codex` target, a collection name, and an
optional destination override. It discovers skills from the selected
collection, refuses to overwrite an existing installation, preserves any
supporting files, and reports actionable errors.

### Cross-harness documentation and metadata

Update the root and collection READMEs to lead with user value, document both
installation paths, and explain the shared-source layout. Retain Claude's
marketplace metadata while making its descriptions and homepage URL neutral.

### Repository identity

Rename the GitHub repository to `agent-skills`, update its description, and
point the local `origin` remote at the new canonical URL after all commits have
been pushed.

## API surface

```text
python3 scripts/install.py codex spec [--dest <skills-directory>]
```

Without `--dest`, installation targets `$CODEX_HOME/skills`, or
`~/.codex/skills` when `CODEX_HOME` is unset.

## Error handling

The installer exits non-zero for an unknown collection, an empty collection,
or any destination skill that already exists. It validates all inputs before
copying so a preflight failure cannot leave a partial installation.

## Testing strategy

- Unit-test frontmatter and command-reference adaptation.
- Run the installer as a subprocess into a temporary directory as an end-to-end
  test, asserting every source skill is installed and invocable by its
  namespaced Codex name.
- Reproduce collision handling through the CLI and verify existing content is
  preserved.
- Keep the existing manifest validator in CI and add the installer test suite.

## Acceptance criteria

- Documentation contains working Claude Code and Codex installation flows.
- Codex receives all collection skills from the canonical source without
  generic-name collisions or Claude-specific invocation references.
- Automated tests fail if installation, transformation, or collision safety
  regresses.
- All repository-owned references use `latere-ai/agent-skills`.
- The GitHub repository and local remote use the neutral name.
