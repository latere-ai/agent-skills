from __future__ import annotations

import importlib.util
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parent.parent
INSTALLER = ROOT / "scripts" / "install.py"
SPEC = importlib.util.spec_from_file_location("agent_skills_installer", INSTALLER)
assert SPEC and SPEC.loader
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class AdaptForCodexTest(unittest.TestCase):
    def test_namespaces_skill_and_invocations(self) -> None:
        source = """---
name: create
description: Create a spec and use /spec:validate when finished.
argument-hint: <track/name>
user-invocable: true
allowed-tools: Read, Write
---

Run /spec:validate, then /spec:review-impl from the /spec:* family.
"""

        adapted = installer.adapt_for_codex(source, "spec", "create")

        self.assertIn("name: spec-create\n", adapted)
        self.assertIn("$spec-validate", adapted)
        self.assertIn("$spec-review-impl", adapted)
        self.assertIn("$spec-*", adapted)
        self.assertNotIn("/spec:", adapted)
        self.assertNotIn("argument-hint:", adapted)
        self.assertNotIn("user-invocable:", adapted)
        self.assertNotIn("allowed-tools:", adapted)

    def test_rejects_missing_frontmatter(self) -> None:
        with self.assertRaisesRegex(installer.InstallError, "no YAML frontmatter"):
            installer.adapt_for_codex("# Create\n", "spec", "create")

    def test_rejects_unterminated_frontmatter(self) -> None:
        with self.assertRaisesRegex(installer.InstallError, "unterminated YAML frontmatter"):
            installer.adapt_for_codex("---\nname: create\n", "spec", "create")

    def test_rejects_frontmatter_without_name(self) -> None:
        with self.assertRaisesRegex(installer.InstallError, "frontmatter has no name"):
            installer.adapt_for_codex("---\ndescription: Create a spec.\n---\n", "spec", "create")


class DestinationTest(unittest.TestCase):
    def test_uses_codex_home(self) -> None:
        with mock.patch.dict(os.environ, {"CODEX_HOME": "/tmp/custom-codex-home"}):
            self.assertEqual(
                installer.codex_skills_dir(),
                pathlib.Path("/tmp/custom-codex-home/skills"),
            )


class InstallerEndToEndTest(unittest.TestCase):
    def run_installer(self, destination: pathlib.Path, collection: str = "spec") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(INSTALLER), "codex", collection, "--dest", str(destination)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_installs_every_source_skill_for_codex(self) -> None:
        source_names = sorted(path.name for path in (ROOT / "plugins/spec/skills").iterdir() if path.is_dir())
        with tempfile.TemporaryDirectory() as directory:
            destination = pathlib.Path(directory) / "skills"

            result = self.run_installer(destination)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f"Installed {len(source_names)} spec skills", result.stdout)
            self.assertEqual(
                sorted(path.name for path in destination.iterdir()),
                [f"spec-{name}" for name in source_names],
            )
            for name in source_names:
                installed = (destination / f"spec-{name}" / "SKILL.md").read_text()
                self.assertIn(f"name: spec-{name}\n", installed)
                self.assertNotIn("/spec:", installed)
                self.assertNotIn("allowed-tools:", installed)

    def test_collision_fails_without_overwriting_existing_skill(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = pathlib.Path(directory) / "skills"
            existing = destination / "spec-create"
            existing.mkdir(parents=True)
            marker = existing / "keep.txt"
            marker.write_text("unchanged")

            result = self.run_installer(destination)

            self.assertEqual(result.returncode, 1)
            self.assertIn("already installed: spec-create", result.stderr)
            self.assertEqual(marker.read_text(), "unchanged")
            self.assertEqual([existing], list(destination.iterdir()))

    def test_unknown_collection_is_actionable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_installer(pathlib.Path(directory), "missing")

        self.assertEqual(result.returncode, 1)
        self.assertIn("error: unknown collection: missing", result.stderr)

    def test_invalid_collection_name_is_actionable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_installer(pathlib.Path(directory), "../spec")

        self.assertEqual(result.returncode, 1)
        self.assertIn("error: invalid collection name: '../spec'", result.stderr)


class DistributionMetadataTest(unittest.TestCase):
    def test_repository_uses_neutral_identity(self) -> None:
        owned_files = [
            ROOT / "README.md",
            ROOT / ".claude-plugin/marketplace.json",
            ROOT / "plugins/spec/.claude-plugin/plugin.json",
            ROOT / "plugins/spec/README.md",
        ]

        for path in owned_files:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertNotIn("claude-plugins", path.read_text())

    def test_root_readme_documents_both_harnesses_and_collections(self) -> None:
        readme = (ROOT / "README.md").read_text()

        self.assertIn("/plugin marketplace add latere-ai/agent-skills", readme)
        collections = sorted(path.name for path in (ROOT / "plugins").iterdir() if path.is_dir())
        for collection in collections:
            with self.subTest(collection=collection):
                self.assertIn(f"python3 scripts/install.py codex {collection}", readme)


if __name__ == "__main__":
    unittest.main()
