#!/usr/bin/env python3
"""Install a skill collection into a supported agent harness."""

from __future__ import annotations

import argparse
import os
import pathlib
import re
import shutil
import sys


ROOT = pathlib.Path(__file__).resolve().parent.parent
CLAUDE_ONLY_FRONTMATTER = {"allowed-tools", "argument-hint", "user-invocable"}
FRONTMATTER_FIELD = re.compile(r"^([A-Za-z][A-Za-z0-9-]*):")
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class InstallError(Exception):
    """An installation error that can be shown directly to a user."""


def codex_skills_dir() -> pathlib.Path:
    codex_home = pathlib.Path(os.environ.get("CODEX_HOME", pathlib.Path.home() / ".codex"))
    return codex_home / "skills"


def adapt_for_codex(text: str, collection: str, skill: str) -> str:
    """Namespace a Claude plugin skill and remove Claude-only metadata."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        raise InstallError(f"{skill}: SKILL.md has no YAML frontmatter")

    end = next(
        (index for index, line in enumerate(lines[1:], start=1) if line.rstrip("\r\n") == "---"),
        None,
    )
    if end is None:
        raise InstallError(f"{skill}: SKILL.md has unterminated YAML frontmatter")

    name = f"{collection}-{skill}"
    header: list[str] = []
    found_name = False
    for line in lines[1:end]:
        match = FRONTMATTER_FIELD.match(line)
        field = match.group(1) if match else None
        if field in CLAUDE_ONLY_FRONTMATTER:
            continue
        if field == "name":
            newline = "\r\n" if line.endswith("\r\n") else "\n"
            header.append(f"name: {name}{newline}")
            found_name = True
        else:
            header.append(line)
    if not found_name:
        raise InstallError(f"{skill}: SKILL.md frontmatter has no name")

    adapted = "".join([lines[0], *header, lines[end], *lines[end + 1 :]])
    command = re.compile(rf"/{re.escape(collection)}:([a-z0-9]+(?:-[a-z0-9]+)*|\*)")
    return command.sub(rf"${collection}-\1", adapted)


def collection_skills(collection: str) -> list[pathlib.Path]:
    if not SKILL_NAME.fullmatch(collection):
        raise InstallError(f"invalid collection name: {collection!r}")
    directory = ROOT / "plugins" / collection / "skills"
    if not directory.is_dir():
        raise InstallError(f"unknown collection: {collection}")
    skills = sorted(path for path in directory.iterdir() if path.is_dir())
    if not skills:
        raise InstallError(f"collection has no skills: {collection}")
    return skills


def install_codex(collection: str, destination: pathlib.Path) -> list[pathlib.Path]:
    skills = collection_skills(collection)
    targets = [destination / f"{collection}-{skill.name}" for skill in skills]
    conflicts = [target for target in targets if target.exists()]
    if conflicts:
        names = ", ".join(target.name for target in conflicts)
        raise InstallError(f"already installed: {names}; remove them before reinstalling")

    adapted: list[tuple[pathlib.Path, str]] = []
    for skill in skills:
        source = skill / "SKILL.md"
        if not source.is_file():
            raise InstallError(f"{skill.relative_to(ROOT)} has no SKILL.md")
        adapted.append((skill, adapt_for_codex(source.read_text(), collection, skill.name)))

    destination.mkdir(parents=True, exist_ok=True)
    for (source, skill_text), target in zip(adapted, targets, strict=True):
        shutil.copytree(source, target)
        (target / "SKILL.md").write_text(skill_text)
    return targets


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("harness", choices=("codex",))
    cli.add_argument("collection", help="collection under plugins/, for example: spec")
    cli.add_argument(
        "--dest",
        type=pathlib.Path,
        default=None,
        help="Codex skills directory (default: $CODEX_HOME/skills or ~/.codex/skills)",
    )
    return cli


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    destination = args.dest or codex_skills_dir()
    try:
        installed = install_codex(args.collection, destination)
    except (InstallError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"Installed {len(installed)} {args.collection} skills for Codex in {destination}")
    print("Restart Codex to load the new skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
