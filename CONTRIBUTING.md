# Contributing

Thank you for improving `agent-skills`. Contributions can add a workflow,
clarify an existing skill, improve harness support, or make the project easier
to adopt.

## Before you start

- Search [existing issues](https://github.com/latere-ai/agent-skills/issues) for
  related work.
- Open a proposal before a large new collection or a change to the spec
  lifecycle. Small documentation and bug fixes can go directly to a pull
  request.
- Do not include credentials, private repository content, or sensitive prompts
  in issues, fixtures, or examples.

## Development setup

The repository has no third-party runtime dependencies. Use Python 3.10 or
newer.

```sh
git clone https://github.com/latere-ai/agent-skills.git
cd agent-skills
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

The first command checks marketplace metadata and skill frontmatter. The test
suite exercises Codex installation, repository portability, and public docs.

## Skill design rules

Skills run inside someone else's repository. Write for that environment.

1. **Route precisely.** The frontmatter `description` must say what the skill
   does and when it should run. Keep `name` equal to the skill directory name.
2. **Read before assuming.** Discover commands, paths, architecture, and
   conventions from the host repository. Do not prescribe one language,
   framework, directory layout, or build tool.
3. **Ground claims in evidence.** Point the agent to real files, manifests, CI
   jobs, or source symbols. Do not invent capabilities or project rules.
4. **Protect user work.** Treat dirty worktrees and existing files as owned by
   the user. Require confirmation before destructive or outward actions.
5. **Make completion verifiable.** Name the tests, checks, artifacts, or review
   evidence needed to call the workflow complete.
6. **Keep one canonical source.** Write Claude Code invocations as
   `/collection:skill`. The Codex installer converts them to
   `$collection-skill` and removes Claude-only frontmatter.

Use direct, audience-appropriate language. User guides should explain value and
usage. Skill instructions should be operational and precise. Comments should
explain technical constraints.

## Add or change a skill

Each skill lives at `plugins/<collection>/skills/<skill>/SKILL.md`.

For a new skill:

1. Create the directory and `SKILL.md`.
2. Add YAML frontmatter with at least `name` and a routing-quality
   `description`.
3. Document the skill in the collection README and usage guide.
4. Add a test for new behavior or for the regression being fixed.
5. Run both validation commands from Development setup.

For a new collection, also add its Claude Code manifest under
`plugins/<collection>/.claude-plugin/`, register it in
`.claude-plugin/marketplace.json`, and add installation and usage guidance.
The Codex installer discovers collections from the `plugins/` tree.

## Test a Codex installation

Use a temporary destination so development does not change your personal Codex
configuration:

```sh
tmp_dir="$(mktemp -d)"
python3 scripts/install.py codex spec --dest "$tmp_dir/skills"
find "$tmp_dir/skills" -maxdepth 2 -name SKILL.md -print
```

Review generated frontmatter and command references in at least one installed
skill. Remove the temporary directory when finished.

## Pull requests

Keep each commit focused and use an imperative subject, for example:

```text
spec: discover repository test commands
docs: explain the large-change workflow
install: reject an invalid collection name
```

A pull request should explain the user problem, the chosen behavior, and how it
was verified. Link any issue or spec that defines the change. Update public docs
when commands, names, lifecycle behavior, or installation steps change.

Maintainers may ask to split a large change when independent concerns can be
reviewed and released separately.

## License

By contributing, you agree that your contribution is licensed under the
[MIT License](LICENSE).
