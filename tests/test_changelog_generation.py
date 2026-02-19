"""Tests for changelog generation helpers in scripts/bump_version.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Import helpers from scripts/bump_version.py without executing main()
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
BUMP_SCRIPT = ROOT / "scripts" / "bump_version.py"


def _import_bump():
    spec = importlib.util.spec_from_file_location("bump_version", BUMP_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["bump_version"] = mod
    spec.loader.exec_module(mod)
    return mod


bv = _import_bump()
Version = bv.Version
_parse = bv._parse_conventional_commit
_build = bv._build_changelog_section


# ---------------------------------------------------------------------------
# _parse_conventional_commit
# ---------------------------------------------------------------------------


class TestParseConventionalCommit:
    def test_feat_no_scope(self):
        p = _parse("abc", "feat: add inference")
        assert p is not None
        assert p.type == "feat"
        assert p.scope is None
        assert p.description == "add inference"
        assert not p.breaking

    def test_fix_with_scope(self):
        p = _parse("abc", "fix(python): null pointer")
        assert p is not None
        assert p.type == "fix"
        assert p.scope == "python"
        assert p.description == "null pointer"

    def test_breaking_change_bang(self):
        p = _parse("abc", "feat(api)!: remove deprecated endpoint")
        assert p is not None
        assert p.breaking is True
        assert p.type == "feat"

    def test_chore_type(self):
        p = _parse("abc", "chore: update lock file")
        assert p is not None
        assert p.type == "chore"

    def test_ci_deps_scope(self):
        p = _parse("abc", "ci(deps): bump actions/checkout from 4 to 6")
        assert p is not None
        assert p.type == "ci"

    def test_merge_commit_skipped(self):
        assert _parse("abc", "Merge pull request #9 from org/branch") is None

    def test_release_commit_skipped(self):
        assert _parse("abc", "release: v0.1.1 (#10)") is None

    def test_plain_commit_skipped(self):
        assert _parse("abc", "just a plain commit message") is None

    def test_case_insensitive_type(self):
        p = _parse("abc", "FEAT: something")
        assert p is not None
        assert p.type == "feat"

    def test_docs_type(self):
        p = _parse("abc", "docs: update API reference")
        assert p is not None
        assert p.type == "docs"

    def test_refactor_type(self):
        p = _parse("abc", "refactor: extract analyzer base class")
        assert p is not None
        assert p.type == "refactor"


# ---------------------------------------------------------------------------
# _build_changelog_section
# ---------------------------------------------------------------------------


class TestBuildChangelogSection:
    V = Version(0, 2, 0)

    def _commits(self, *subjects: str) -> list[tuple[str, str]]:
        return [("abc1234", s) for s in subjects]

    def test_contains_version_header(self):
        section = _build(
            self.V,
            self._commits("feat: add something"),
            include_maintenance=False,
        )
        assert "## [0.2.0]" in section

    def test_feat_goes_to_added(self):
        section = _build(
            self.V,
            self._commits("feat: new thing"),
            include_maintenance=False,
        )
        assert "### Added" in section
        assert "new thing" in section

    def test_fix_goes_to_fixed(self):
        section = _build(
            self.V,
            self._commits("fix: crash fix"),
            include_maintenance=False,
        )
        assert "### Fixed" in section
        assert "crash fix" in section

    def test_refactor_goes_to_changed(self):
        section = _build(
            self.V,
            self._commits("refactor: clean up"),
            include_maintenance=False,
        )
        assert "### Changed" in section

    def test_docs_goes_to_documentation(self):
        section = _build(
            self.V,
            self._commits("docs: update readme"),
            include_maintenance=False,
        )
        assert "### Documentation" in section

    def test_maintenance_hidden_by_default(self):
        section = _build(
            self.V,
            self._commits("chore: update lock"),
            include_maintenance=False,
        )
        assert "### Maintenance" not in section

    def test_maintenance_shown_with_flag(self):
        section = _build(
            self.V,
            self._commits("chore: update lock"),
            include_maintenance=True,
        )
        assert "### Maintenance" in section
        assert "update lock" in section

    def test_breaking_change_at_top(self):
        section = _build(
            self.V,
            self._commits("feat(api)!: remove endpoint", "fix: small fix"),
            include_maintenance=False,
        )
        breaking_pos = section.index("Breaking Changes")
        fixed_pos = section.index("### Fixed")
        assert breaking_pos < fixed_pos

    def test_empty_log_placeholder(self):
        section = _build(self.V, [], include_maintenance=False)
        assert "No notable changes" in section

    def test_merge_commits_skipped(self):
        section = _build(
            self.V,
            self._commits("Merge pull request #1 from org/branch"),
            include_maintenance=False,
        )
        assert "Merge pull request" not in section

    def test_scope_rendered_bold(self):
        section = _build(
            self.V,
            self._commits("fix(python): null ptr"),
            include_maintenance=False,
        )
        assert "**python**" in section

    def test_multiple_sections(self):
        section = _build(
            self.V,
            self._commits("feat: feature one", "fix: bugfix one", "docs: readme"),
            include_maintenance=False,
        )
        assert "### Added" in section
        assert "### Fixed" in section
        assert "### Documentation" in section

    def test_ci_deps_excluded_without_maintenance_flag(self):
        section = _build(
            self.V,
            self._commits("ci(deps): bump actions/checkout from 4 to 6"),
            include_maintenance=False,
        )
        assert "### Maintenance" not in section

    def test_date_present_in_header(self):
        import datetime

        today = datetime.datetime.now(datetime.UTC).date().isoformat()
        section = _build(self.V, self._commits("feat: x"), include_maintenance=False)
        assert today in section
