# Continuous integration kit

The `ci` collection covers the last two steps of a change: getting it into the
repository as reviewable commits, and getting a version of it into production
with proof that it arrived.

Start with the [task-oriented usage guide](../../docs/ci-kit.md). This page is
the technical reference for installation, the contract each skill works to, and
what it refuses to do.

## Install

| Harness | Installation |
| --- | --- |
| Claude Code | `/plugin marketplace add latere-ai/agent-skills`, then `/plugin install ci@latere-ai` |
| Codex | Clone `latere-ai/agent-skills`, then run `python3 scripts/install.py codex ci` |

Claude Code exposes `/ci:<skill>`. Codex exposes the same workflow as
`$ci-<skill>`. Arguments and behavior are otherwise equivalent.

## Core contract

- The repository is the source of truth. Both skills read `AGENTS.md`,
  `CLAUDE.md`, `CONTRIBUTING.md`, and CI configuration before acting, and those
  instructions outrank the skills.
- Nothing is discovered once and cached. Each run re-reads the repository, so a
  changed release pipeline is picked up without configuration.
- Outward-facing steps ask first. Pushing a tag is confirmed with the user
  because it is the last reversible moment.
- Evidence, not optimism. A release is reported as shipped only when the
  pipeline finished successfully and the deployed environment answers.

## Skills

### `commit-and-push`

Groups a working tree into one commit per logical change, stages by explicit
path, and pushes once.

- Files are staged individually. `git add -A` and `git add .` are prohibited,
  because they sweep unrelated work and untracked files into a review unit.
- A fix and its test, or a feature and its documentation, are one commit. A
  formatting sweep or a dependency bump is its own commit.
- Untracked files are decided one at a time and anything left out is reported.
- No attribution trailers are added unless the repository asks for them.

### `tag-and-release`

Cuts a release by tagging a proven commit, then verifies the release actually
landed.

It first learns how the repository releases: the tag scheme in use, what a tag
push triggers, where that deploys, and any release rules the repository states.
If nothing releases on a tag, it stops and asks rather than inventing a
mechanism.

Preflight gates, each a hard stop:

| Gate | Requirement |
| --- | --- |
| Clean tree | `git status --porcelain` is empty |
| Right branch | the branch the release pipeline builds from |
| Pushed | the commit exists on the remote branch |
| CI green | every gating run for **that exact SHA** completed with success |
| Free version | the tag exists neither locally nor on the remote |
| Non-empty | at least one commit since the last tag |

A pending run is not a green run, and a status that cannot be retrieved is a
failed gate rather than a passed one.

After the tag is pushed it waits for the release pipeline, then verifies what
the pipeline promised: the run's conclusion, the release object, the deployed
environment's health endpoint, and — where the service exposes a version — that
the live version is the one just tagged. Anything it could not check is named in
the report instead of being implied.

## Requirements

- Git, and a remote the agent can push to.
- A repository that releases from a tag push, for `tag-and-release`.
- A command-line client for the host's CI, such as `gh` for GitHub, so run
  status can be queried per commit.

## License

MIT. See [LICENSE](LICENSE).
