# Latere AI agent skills

Reusable workflows built at [Latere AI](https://latere.ai), packaged from one
source for Claude Code and Codex.

## Install for Claude Code

```
/plugin marketplace add latere-ai/agent-skills
/plugin install spec@latere-ai
```

## Install for Codex

```sh
git clone https://github.com/latere-ai/agent-skills.git
cd agent-skills
python3 scripts/install.py codex spec
```

The installer adds namespaced skills such as `$spec-create`, `$spec-implement`,
and `$spec-drive` to `$CODEX_HOME/skills` (or `~/.codex/skills`) without
overwriting existing skills. They are available on the next Codex turn.

## Collections

| Collection | Claude Code | Codex | What it is |
| --- | --- | --- | --- |
| [spec](plugins/spec) | `/plugin install spec@latere-ai` | `python3 scripts/install.py codex spec` | Drive design specs through a seven-state lifecycle and a dependency DAG, from idea to verified delivery |

## Layout

```
.claude-plugin/marketplace.json   Claude Code marketplace adapter
plugins/<name>/
  .claude-plugin/plugin.json      Claude Code collection adapter
  skills/<skill>/SKILL.md         canonical, shared skill source
  README.md
scripts/install.py                harness-specific installation adapter
```

Harness adapters may namespace commands or omit harness-specific metadata, but
the workflow instructions stay in the canonical skill source.

## Contributing

Skills are prose, and prose drifts from the systems it describes. A change that
states a rule the code enforces should say where that rule lives, so a reader
can check it. Keep skills repository-agnostic: read conventions off the tree
being worked on rather than naming a fixed set.

## License

MIT
