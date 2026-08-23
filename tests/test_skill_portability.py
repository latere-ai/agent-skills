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

    def test_skills_name_no_private_sibling_repository(self) -> None:
        """Skill bodies ship to every user, so an example path must be generic.

        A relative path into a named sibling checkout only resolves on the
        maintainer's machine and publishes that repository's name.
        """
        forbidden = (
            "../lux/",
            "../agents/",
            "../auth/",
            "../sandbox/",
            "../platform/",
        )

        for path in (ROOT / "plugins").glob("*/skills/*/SKILL.md"):
            text = path.read_text()
            for phrase in forbidden:
                with self.subTest(skill=path.parent.name, phrase=phrase):
                    self.assertNotIn(phrase, text)

    def test_spec_template_does_not_hardcode_an_author(self) -> None:
        """The frontmatter template is copied verbatim into a user's spec.

        A literal maintainer handle here stamps that name onto every spec the
        skill creates in someone else's repository.
        """
        for path in (ROOT / "plugins").glob("*/skills/*/SKILL.md"):
            with self.subTest(skill=path.parent.name):
                self.assertNotIn("author: changkun", path.read_text())

    def test_release_skill_keeps_its_two_guarantees(self) -> None:
        """The whole point of the skill is prose an edit could quietly drop.

        Both guarantees are checked by the phrase that implements them: the CI
        gate must query one commit rather than a branch, must not accept a run
        that is still going, and the release must be verified against what is
        actually live afterwards.
        """
        skill = (ROOT / "plugins/ci/skills/tag-and-release/SKILL.md").read_text()

        for phrase in (
            "gh run list --commit",  # green on this commit, not on the branch
            "in_progress",  # a pending run is not a green run
            "gh run watch",  # wait for the release run rather than assuming
            "gh release view",  # the release object exists
            "version",  # what is live reports the tag just pushed
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill)


if __name__ == "__main__":
    unittest.main()
