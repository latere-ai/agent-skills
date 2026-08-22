from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parent.parent


class SkillPortabilityTest(unittest.TestCase):
    def test_skills_do_not_assume_one_application_stack(self) -> None:
        forbidden = (
            "internal/apicontract/routes.go",
            "make api-contract",
            "make test-frontend",
            "go vet ./...",
            "go test ./...",
            "frontend/src/",
            "Pinia stores",
            "per-task directory storage",
            "make test",
            "make build",
            "wallfacer is the reference implementation",
        )

        for path in (ROOT / "plugins").glob("*/skills/*/SKILL.md"):
            text = path.read_text()
            for phrase in forbidden:
                with self.subTest(skill=path.parent.name, phrase=phrase):
                    self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
