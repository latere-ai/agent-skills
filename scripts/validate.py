#!/usr/bin/env python3
"""Check that the marketplace, its plugins, and their skills agree.

Claude Code fails quietly on a malformed plugin: a skill whose frontmatter
`name` does not match its directory, or a plugin the marketplace points at but
that carries no manifest, simply does not appear. These checks turn that into a
build failure instead.
"""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def frontmatter(path: pathlib.Path) -> dict[str, str]:
    """Parse the leading --- fenced block. Values are single-line scalars."""
    text = path.read_text()
    if not text.startswith("---\n"):
        fail(f"{path.relative_to(ROOT)}: no YAML frontmatter")
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        fail(f"{path.relative_to(ROOT)}: unterminated frontmatter")
        return {}
    out = {}
    for line in text[4:end].split("\n"):
        m = re.match(r"^([a-zA-Z-]+):\s*(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


market_path = ROOT / ".claude-plugin" / "marketplace.json"
market = json.loads(market_path.read_text())

for key in ("name", "owner", "plugins"):
    if key not in market:
        fail(f"marketplace.json: missing {key!r}")

for entry in market.get("plugins", []):
    name = entry.get("name", "<unnamed>")
    src = ROOT / entry.get("source", "")
    manifest = src / ".claude-plugin" / "plugin.json"
    if not manifest.is_file():
        fail(f"plugin {name!r}: no manifest at {manifest.relative_to(ROOT)}")
        continue

    plugin = json.loads(manifest.read_text())
    if plugin.get("name") != name:
        fail(f"plugin {name!r}: manifest name is {plugin.get('name')!r}")
    if plugin.get("version") != entry.get("version"):
        fail(
            f"plugin {name!r}: marketplace lists version {entry.get('version')!r}, "
            f"manifest says {plugin.get('version')!r}"
        )

    skills = src / "skills"
    if not skills.is_dir():
        continue
    seen = 0
    for d in sorted(p for p in skills.iterdir() if p.is_dir()):
        seen += 1
        f = d / "SKILL.md"
        if not f.is_file():
            fail(f"skill {d.name!r}: no SKILL.md")
            continue
        fm = frontmatter(f)
        if fm.get("name") != d.name:
            fail(f"skill {d.name!r}: frontmatter name is {fm.get('name')!r}")
        desc = fm.get("description", "")
        if not desc:
            fail(f"skill {d.name!r}: empty description — nothing routes to it")
        elif len(desc) < 40:
            fail(f"skill {d.name!r}: description too thin to route on ({len(desc)} chars)")
    if seen == 0:
        fail(f"plugin {name!r}: no skills")
    print(f"plugin {name}: {seen} skills")

for e in errors:
    print(f"error: {e}", file=sys.stderr)
sys.exit(1 if errors else 0)
