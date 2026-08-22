# Agent skills from Latere AI

[![Validate](https://github.com/latere-ai/agent-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/latere-ai/agent-skills/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/github/license/latere-ai/agent-skills)](LICENSE)

Reusable workflows for coding agents. Install one collection and use the same
process in Claude Code or Codex.

The first collection, **spec**, turns a change request into a durable design,
an explicit dependency graph, a tested implementation, and a recorded outcome.
The work stays in your repository, where your team can review it with the code.

## Why use it

Agent chats are useful working memory, but they are a poor system of record.
This project gives agents a file-based workflow for work that must survive a
session, cross package boundaries, or be reviewed by other people.

- **Review intent before code:** design, scope, risks, and acceptance criteria
  live in Markdown.
- **Make dependencies visible:** `depends_on` forms one directed graph across
  the spec tree.
- **Require completion evidence:** a spec passes through a testing verdict
  before it can become complete.
- **Keep your repository authoritative:** skills discover local instructions,
  commands, tests, and documentation conventions.
- **Avoid harness lock-in:** canonical skill sources are adapted for Claude Code
  and Codex during installation.

## Quick start

### Claude Code

Add the marketplace and install the collection:

```text
/plugin marketplace add latere-ai/agent-skills
/plugin install spec@latere-ai
```

Create your first spec:

```text
/spec:create product/cache-warming Add bounded cache warming so first requests avoid the full load cost
```

### Codex

Clone the repository and run the installer with Python 3.10 or newer:

```sh
git clone https://github.com/latere-ai/agent-skills.git
cd agent-skills
python3 scripts/install.py codex spec
```

Start a new Codex turn, then create your first spec:

```text
$spec-create product/cache-warming Add bounded cache warming so first requests avoid the full load cost
```

The installer writes namespaced skills such as `$spec-create`,
`$spec-implement`, and `$spec-drive` to `$CODEX_HOME/skills`, or
`~/.codex/skills` when `CODEX_HOME` is unset. It refuses to overwrite existing
skills.

### Take the spec to completion

Both create commands report the generated spec path. Review that file, then
give the path to the lifecycle orchestrator:

| Claude Code | Codex |
| --- | --- |
| `/spec:drive specs/cache-warming.md` | `$spec-drive specs/cache-warming.md` |

`drive` selects the next legal step based on the spec's status. It can validate,
break down, implement, review, and wrap up the work. It pauses before outward or
hard-to-reverse actions.

Read [Using the spec kit](docs/spec-kit.md) for small and large change paths,
the seven-state lifecycle, team conventions, command reference, and
troubleshooting.

## Collections

| Collection | What you get | Guide |
| --- | --- | --- |
| [spec](plugins/spec) | 14 skills for design, dependency planning, implementation, review, drift detection, and lifecycle reporting | [Usage guide](docs/spec-kit.md) |

## Contributing

Contributions are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md) for
skill design rules, local checks, and pull-request expectations. By
participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

Use [GitHub Issues](https://github.com/latere-ai/agent-skills/issues) for bugs
and proposals. Report sensitive vulnerabilities through the process in
[SECURITY.md](SECURITY.md).

## License

Licensed under the [MIT License](LICENSE).
