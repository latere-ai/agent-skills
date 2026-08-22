from __future__ import annotations

import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parent.parent
# Each collection under plugins/ and the guide that teaches it.
GUIDES = {
    "spec": "docs/spec-kit.md",
    "ci": "docs/ci-kit.md",
}
PUBLIC_DOCS = (
    ROOT / "README.md",
    ROOT / "plugins/spec/README.md",
    ROOT / "plugins/ci/README.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "CODE_OF_CONDUCT.md",
    ROOT / "SECURITY.md",
)


class OpenSourceProjectTest(unittest.TestCase):
    def test_required_community_files_exist(self) -> None:
        for path in PUBLIC_DOCS:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())
        self.assertTrue((ROOT / ".github/ISSUE_TEMPLATE/bug.yml").is_file())
        self.assertTrue((ROOT / ".github/ISSUE_TEMPLATE/feature.yml").is_file())
        self.assertTrue((ROOT / ".github/PULL_REQUEST_TEMPLATE.md").is_file())

    def test_every_collection_has_a_guide(self) -> None:
        collections = sorted(p.name for p in (ROOT / "plugins").iterdir() if p.is_dir())
        self.assertEqual(collections, sorted(GUIDES))
        for guide in GUIDES.values():
            with self.subTest(guide=guide):
                self.assertTrue((ROOT / guide).is_file())

    def test_readme_has_status_badges_and_usage_guide(self) -> None:
        readme = (ROOT / "README.md").read_text()

        self.assertIn("actions/workflows/validate.yml/badge.svg", readme)
        self.assertIn("img.shields.io/github/license/latere-ai/agent-skills", readme)
        self.assertIn("docs/spec-kit.md", readme)
        self.assertIn("## Quick start", readme)

    def test_public_guides_include_renderable_workflow_diagrams(self) -> None:
        readme = (ROOT / "README.md").read_text()
        guide = (ROOT / "docs/spec-kit.md").read_text()

        self.assertNotIn("```mermaid", readme)
        self.assertIn("```mermaid\nflowchart", guide)
        self.assertIn("```mermaid\nstateDiagram-v2", guide)

    def test_each_guide_covers_every_skill_in_its_collection(self) -> None:
        """A skill missing from its guide is a skill nobody knows to invoke."""
        for collection, guide_path in GUIDES.items():
            guide = (ROOT / guide_path).read_text()
            skills = ROOT / "plugins" / collection / "skills"
            names = sorted(path.name for path in skills.iterdir() if path.is_dir())
            self.assertTrue(names, f"{collection}: no skills")

            for name in names:
                with self.subTest(collection=collection, skill=name):
                    self.assertIn(f"`/{collection}:{name}`", guide)
                    self.assertIn(f"`${collection}-{name}`", guide)

    def test_readme_lists_every_collection(self) -> None:
        readme = (ROOT / "README.md").read_text()
        for collection, guide_path in GUIDES.items():
            with self.subTest(collection=collection):
                self.assertIn(f"plugins/{collection}", readme)
                self.assertIn(guide_path, readme)

    def test_public_markdown_links_resolve(self) -> None:
        markdown = [path for path in PUBLIC_DOCS if path.is_file()]
        docs = ROOT / "docs"
        if docs.is_dir():
            markdown.extend(docs.rglob("*.md"))

        for path in markdown:
            for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", path.read_text()):
                if target.startswith(("https://", "http://", "mailto:", "#")):
                    continue
                local = target.split("#", 1)[0]
                with self.subTest(path=path.relative_to(ROOT), target=target):
                    self.assertTrue((path.parent / local).resolve().exists())

if __name__ == "__main__":
    unittest.main()
