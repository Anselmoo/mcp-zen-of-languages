import sys

from pathlib import Path


repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

from scripts.check_tool_version_agreement import _disagreements  # noqa: E402
from scripts.check_tool_version_agreement import _normalise  # noqa: E402
from scripts.check_tool_version_agreement import collect_versions  # noqa: E402
from scripts.check_tool_version_agreement import main  # noqa: E402


def test_normalise_strips_leading_v() -> None:
    assert _normalise("v1.17.1") == "1.17.1"
    assert _normalise("1.17.1") == "1.17.1"


def test_normalise_keeps_inner_v() -> None:
    # Only a *leading* v is a tag prefix; a v elsewhere is part of the version.
    assert _normalise("0.16.6dev1") == "0.16.6dev1"


def test_disagreements_empty_when_all_sources_agree() -> None:
    collected = {
        "ruff": {"pre-commit rev": "0.16.6", "uv.lock": "0.16.6"},
        "repo-release-tools": {"pre-commit rev": "1.17.1", "CI action": "1.17.1"},
    }
    assert _disagreements(collected) == []


def test_disagreements_detects_a_mismatch() -> None:
    # This is the case the guard exists for: the pre-commit hook and the
    # binary uv resolves are different builds of the same linter.
    collected = {"ruff": {"pre-commit rev": "0.16.6", "uv.lock": "0.15.18"}}

    result = _disagreements(collected)

    assert len(result) == 1
    tool, sources = result[0]
    assert tool == "ruff"
    assert sources == {"pre-commit rev": "0.16.6", "uv.lock": "0.15.18"}


def test_disagreements_flags_three_way_split() -> None:
    collected = {
        "repo-release-tools": {
            "pre-commit rev": "1.17.1",
            "uv.lock": "1.9.0",
            "CI action": "1.8.1",
        },
    }

    assert [tool for tool, _ in _disagreements(collected)] == ["repo-release-tools"]


def test_disagreements_ignores_tool_pinned_in_only_one_place() -> None:
    # A single pin cannot disagree with itself, so it is not a finding.
    collected = {"ruff": {"uv.lock": "0.16.6"}}
    assert _disagreements(collected) == []


def test_collect_versions_finds_both_tools_in_this_repo() -> None:
    collected = collect_versions(repo_root)

    assert set(collected) == {"ruff", "repo-release-tools"}
    # ruff is pinned by the hook and resolved in the lock.
    assert {"pre-commit rev", "uv.lock"} <= set(collected["ruff"])
    # rrt adds a third pin: the CI action.
    assert {"pre-commit rev", "uv.lock", "CI action"} == set(
        collected["repo-release-tools"],
    )


def test_tool_versions_agree_in_this_repo() -> None:
    assert main() == 0
