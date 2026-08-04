# Latere AI plugins for Claude Code

A marketplace of Claude Code plugins built at [Latere AI](https://latere.ai).

```
/plugin marketplace add latere-ai/claude-plugins
```

## Plugins

| Plugin | Install | What it is |
| --- | --- | --- |
| [spec](plugins/spec) | `/plugin install spec@latere-ai` | Spec-driven development: design specs with a seven-state lifecycle, decomposed into a dependency DAG, driven from idea to shipped |

## Layout

```
.claude-plugin/marketplace.json   the marketplace manifest
plugins/<name>/
  .claude-plugin/plugin.json      the plugin manifest
  skills/<skill>/SKILL.md         one directory per skill
  README.md
```

## Contributing

Skills are prose, and prose drifts from the systems it describes. A change that
states a rule the code enforces should say where that rule lives, so a reader
can check it. Keep skills repository-agnostic: read conventions off the tree
being worked on rather than naming a fixed set.

## License

MIT
