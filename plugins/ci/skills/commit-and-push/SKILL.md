---
name: commit-and-push
description: Commit the working tree as one commit per logical change, staging files explicitly, then push once. Use when work is finished and should reach the remote as reviewable units rather than a single mixed commit.
argument-hint: [scope or message hint]
allowed-tools: Read, Grep, Glob, Bash(git *)
---

# Commit and Push

Turn an untidy working tree into a sequence of commits a reviewer can read one
at a time, then push once.

A commit is a unit of review, not a save point. Two unrelated changes in one
commit cannot be reviewed, reverted, or bisected separately, so the work of this
skill is mostly deciding where the boundaries are.

## Step 0: Read the repository's own rules

Repository instructions outrank anything written here. Before staging, read
whichever of these exist: `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, and any
commit or Git conventions they point to.

Look for, and obey:

- **Message format** — a required prefix, scope, issue reference, or sign-off.
- **Branch policy** — whether the default branch takes direct pushes or work
  belongs on a branch with a pull request.
- **Staging rules** — many repositories forbid `git add -A` and `git add .`.
- **Pre-commit checks** — tests, formatters, or linters expected to pass first.

If the repository says nothing about branch policy and the current branch is the
default branch, ask before pushing to it.

## Step 1: See everything that changed

```bash
git status --porcelain
git diff
git diff --staged
git log --oneline -10
```

Read the recent log for the house style: message length, mood, capitalisation,
whether bodies are used. Match it. A commit that reads differently from its
neighbours is noise for every future reader of the log.

If something is already staged, treat that as a hint about an intended grouping,
not as a decision — regroup if it mixes concerns.

## Step 2: Group changes into logical units

One commit is one change of intent. Split by intent, not by file or by
directory:

- a bug fix and its regression test belong together;
- a feature and the documentation describing it belong together;
- a rename that touches thirty files is one commit;
- a formatting sweep is its own commit, never mixed with behaviour;
- a dependency bump is its own commit.

Untracked files need a decision each. Include a file only when it belongs to the
work being committed. Leave build output, local scratch files, credentials, and
anything the repository's ignore rules should have covered — and say so in your
report rather than committing them silently. If a file looks like it was meant
to be ignored, propose an ignore-rule change instead of adding the file.

## Step 3: Commit each unit

For each group, in an order that keeps the tree buildable at every step:

1. Stage that group's paths **explicitly**: `git add path/one path/two`. Never
   `git add -A`, never `git add .`, never `git commit -a`.
2. Confirm what is staged: `git diff --staged --stat`.
3. Write the message:
   - a subject line that names the change and its effect, in the repository's
     style;
   - a body only when the change needs a reason, a trade-off, or a consequence
     recorded. Say why, not what — the diff already says what.
4. Commit.

Never add a `Co-Authored-By` trailer or any other attribution trailer unless the
repository's conventions require one. Keep the human author.

If a pre-commit hook rejects the commit, fix the cause and commit again. Do not
pass `--no-verify` unless the user explicitly asks for it.

## Step 4: Push once

Push after all commits exist, so the remote sees a coherent series:

```bash
git push origin <branch>
```

If the branch has no upstream, set it: `git push -u origin <branch>`.

If the push is rejected because the remote moved on, integrate first with the
repository's stated strategy (rebase or merge) and re-run the repository's
checks before pushing again. Never force-push a shared branch. Only use
`--force-with-lease`, and only on a branch that is yours, and only when the user
asked for it.

## Step 5: Report

State, briefly:

- each commit as `<short sha> <subject>`;
- what was deliberately left uncommitted, and why;
- the branch and remote that now hold the work.

## Rules

- One commit is one logical change. Never bundle unrelated changes.
- Stage by path. `git add -A` and `git add .` are prohibited.
- Repository conventions outrank this skill.
- Never amend or rebase commits that are already pushed unless asked.
- Never invent a change to make a commit look tidy; commit what exists.
