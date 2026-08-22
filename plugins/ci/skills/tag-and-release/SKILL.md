---
name: tag-and-release
description: Cut a release by pushing a version tag, but only after proving CI is green on the exact commit being tagged, then watch the pipeline and confirm the new version is actually live before reporting success. Use when a repository releases by tag.
argument-hint: [version | major|minor|patch] [--notes <file>]
allowed-tools: Read, Grep, Glob, Bash(git *), Bash(gh *), Bash(glab *), Bash(curl *), Bash(ls *), Bash(cat *)
---

# Tag and Release

Release the current commit by tagging it, and do not claim it shipped until the
pipeline says it shipped and the deployed service agrees.

Two failures this skill exists to prevent:

- **Tagging a commit that was never proven.** "The last CI run was green" is not
  the same as "CI is green on this commit". A tag on an untested commit is a
  release nobody can trust.
- **Reporting a release that never landed.** A pushed tag starts a pipeline; it
  is not evidence the pipeline finished, the deployment rolled, or the service
  came back. Success is verified at the far end, or it is not claimed.

A tag is close to irreversible: it triggers deployment, it is what other people
pin to, and deleting a published one breaks anyone who already fetched it. Treat
every step as outward-facing.

## Step 0: Parse arguments

`$ARGUMENTS` may contain, in any order:

- an explicit version (`v1.4.0`, `1.4.0`) — use exactly this, only normalising
  the prefix to match existing tags;
- a bump level (`major`, `minor`, `patch`) — compute the next version from the
  latest tag;
- `--notes <file>` — take the tag message body from that file instead of writing
  one from the commit log.

With no arguments, propose a version yourself in Step 3.

## Step 1: Learn how this repository releases

Never assume a mechanism. Read it out of the repository:

1. **Tag scheme** — `git tag --sort=-v:refname | head -20`. Note the prefix
   (`v` or none), whether pre-release or channel suffixes are used, and whether
   patch tags exist at all. Read the newest annotated tag's message with
   `git tag -n99 <tag>`: that is the house format for release notes.
2. **What a tag triggers** — search the CI configuration for tag triggers, for
   example `on: push: tags:` in `.github/workflows/*.yml`, `rules:` on
   `$CI_COMMIT_TAG` in `.gitlab-ci.yml`, or the equivalent for the host in use.
   Read the workflow: what it builds, where it deploys, and whether it publishes
   a release object.
3. **Where it deploys** — the workflow, deployment manifests, or README usually
   name the environment and its URL. Note any health, version, or status
   endpoint. Note the smoke test the pipeline runs, and what it asserts.
4. **Release rules the repository states** — `AGENTS.md`, `CLAUDE.md`,
   `CONTRIBUTING.md`, `RELEASING.md`, or a changelog convention. If a changelog
   file is maintained by hand, it must be updated and committed **before** the
   tag, not after.

If nothing in the repository releases on a tag, stop. Report what you looked at
and ask how this repository is meant to release. Do not invent a pipeline, and
do not push a tag hoping something reacts to it.

## Step 2: Preflight gates

Every gate is a hard stop. A gate that cannot be evaluated is a failed gate, not
a passed one. Report which gate failed and what would clear it.

1. **Clean tree** — `git status --porcelain` is empty. Uncommitted work is not in
   the release, and a dirty tree usually means something was forgotten.
2. **Right branch** — the current branch is the one the release pipeline builds
   from (usually the default branch). If it is not, stop.
3. **In sync with the remote** — `git fetch origin`, then confirm the local
   branch and its upstream point at the same commit. Never tag a commit the
   remote does not have: `git branch -r --contains HEAD` must list the upstream
   branch.
4. **CI green on this exact commit** — resolve `sha=$(git rev-parse HEAD)` and
   ask the host about that SHA, not about the branch:

   ```bash
   gh run list --commit "$sha" --json workflowName,event,status,conclusion
   ```

   Requirements:
   - at least one run exists for that SHA — no runs means nothing was proven;
   - every run that gates merges has `status: completed` and
     `conclusion: success`;
   - a run still `in_progress` or `queued` is not green. Either wait for it and
     re-check, or stop. Never tag past a pending run.

   Treat `failure`, `cancelled`, `timed_out`, and `action_required` as red.
   Workflows that are cosmetic for this purpose (for example a nightly job
   unrelated to the build) may be excluded only if you name them in your report.

   If the host is not GitHub, use its equivalent commit-status query. If no
   status can be retrieved at all, stop and say so.
5. **Version not already used** — the proposed tag exists neither locally nor on
   the remote: `git tag -l <tag>` and `git ls-remote --tags origin <tag>` are
   both empty. Never move or re-point an existing tag.
6. **Something to release** — there is at least one commit since the last tag.
   If there is none, ask whether a re-release is really intended.

## Step 3: Choose the version and write the notes

1. List what is being released: `git log --oneline <last-tag>..HEAD`.
2. Choose the next version under the repository's scheme, honouring an explicit
   argument. With no argument, propose one and justify it in a sentence:
   breaking or removed behaviour is a major bump, new user-visible behaviour is
   a minor bump, and fixes or behaviour-preserving changes are a patch bump. Say
   which commits drove the choice.
3. Draft the annotated tag message in the format the previous tags use, unless
   `--notes` supplied one. It is the release note, so write it for the people
   who will read the release, not for the committer: what changed, why it
   matters, and anything an operator must know. Keep repository-internal
   shorthand out of it.
4. Check for release prerequisites the repository states: a changelog entry, a
   version constant, a manifest version. If one exists and is stale, update and
   commit it first, then return to Step 2 — the CI gate must pass on the commit
   you are actually going to tag.

## Step 4: Confirm, then tag

Show the user, in one message: the version, the commit being tagged, the commits
included, the tag message, and what pushing will trigger (which pipeline, which
environment, which URL). Ask for confirmation and wait for it.

On approval, create an annotated tag — pass the message on stdin so no scratch
file is needed:

```bash
git tag -a <tag> -F - <<'EOF'
<subject line>

<body>
EOF
git push origin <tag>
```

If the push fails, stop and report; do not retry with a different version to get
around it.

## Step 5: Prove it released

This step is not optional, and its result is the answer the user asked for.

1. **Find the run the tag started, by the tag.** A tag-triggered run carries the
   tag in the ref it was built from, so query on that. Do not match on the run's
   title: for a tag push it shows the tagged commit's subject, which is also the
   title of the branch run that preceded it.

   ```bash
   gh run list --branch <tag> --json databaseId,workflowName,status,conclusion,url
   ```

   The run may take a few seconds to appear. An empty result means the tag
   triggered nothing — re-read what you found in Step 1 rather than waiting
   indefinitely.

2. **Wait for it to finish**, with the command built for waiting:

   ```bash
   gh run watch <run-id> --exit-status
   ```

   It blocks until the run completes and exits non-zero if the run failed. If
   the host has no such command, poll — but note that an agent harness may
   refuse a blocking `sleep` in the foreground, so run the wait loop in the
   background and read its result, rather than issuing bare polls that each
   return immediately and read as "not finished yet". Never report a result
   while the run is `queued` or `in_progress`.

3. **Judge the outcome.**
   - `success` — continue to verification.
   - anything else — the release failed. Fetch the failing job and the last
     lines of its log (`gh run view <id> --log-failed`), report what broke, and
     state plainly that the tag exists but nothing shipped. Do not delete the
     tag on your own initiative; ask whether to fix forward with a new version
     or to remove the tag.

4. **Verify the artifacts the pipeline promised**, whichever apply:
   - the release object exists and is not a draft:
     `gh release view <tag> --json tagName,isDraft,publishedAt`;
   - the published image, package, or binary the workflow claims to produce is
     retrievable;
   - the deployed environment answers: request its health or status endpoint and
     require a success status, not merely a reachable host;
   - **the live version is the new version** — if the service exposes a version,
     build, or commit endpoint, require it to report the tag just pushed. This
     is the only check that distinguishes "deployment rolled" from "old pods
     still serving". If no such endpoint exists, say so in the report rather
     than implying the version was confirmed.

5. **Report the verdict** with evidence: the tag, the run URL and conclusion, the
   release URL, and each verification with what it returned. If any check could
   not be run, name it and say why. Never summarise an unverified release as
   released.

## Rules

- A red or pending CI result is a stop, never a warning to note and pass.
- Confirm with the user before the tag is pushed. That is the last reversible
  moment.
- One tag, one commit, one version. Never move, re-point, or force-push a tag,
  and never delete a published one without an explicit instruction.
- The tag message is the release note; write it for its readers.
- Verify at the far end. "The workflow started" is not a release.
- If the pipeline fails after the tag is pushed, say so directly and leave the
  repository in a state the user can act on.
