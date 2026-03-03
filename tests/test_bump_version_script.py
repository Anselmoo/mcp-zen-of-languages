"""Tests for branch-conflict helpers in scripts/bump_version.py."""

from __future__ import annotations

import importlib.util
import sys

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
BUMP_SCRIPT = ROOT / "scripts" / "bump_version.py"


def _import_bump():
    spec = importlib.util.spec_from_file_location("bump_version", BUMP_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["bump_version"] = mod
    spec.loader.exec_module(mod)
    return mod


bv = _import_bump()


class TestConfirmBranchOverwrite:
    def test_yes_returns_true(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _prompt: "y")
        assert bv._confirm_branch_overwrite("release/v1.2.3") is True

    def test_empty_returns_false(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _prompt: "")
        assert bv._confirm_branch_overwrite("release/v1.2.3") is False

    def test_retries_on_invalid_input(self, monkeypatch, capsys):
        responses = iter(["maybe", "yes"])
        monkeypatch.setattr("builtins.input", lambda _prompt: next(responses))
        assert bv._confirm_branch_overwrite("release/v1.2.3") is True
        assert "Please answer 'y' or 'n'." in capsys.readouterr().out


class TestPrepareReleaseBranch:
    def test_skips_when_branch_does_not_exist(self, monkeypatch):
        monkeypatch.setattr(bv, "_branch_exists", lambda _branch: False)
        bv._prepare_release_branch("release/v1.2.3", base="main", dry_run=False)

    def test_aborts_when_user_declines_overwrite(self, monkeypatch):
        monkeypatch.setattr(bv, "_branch_exists", lambda _branch: True)
        monkeypatch.setattr(bv, "_confirm_branch_overwrite", lambda _branch: False)
        with pytest.raises(SystemExit, match="1"):
            bv._prepare_release_branch("release/v1.2.3", base="main", dry_run=False)

    def test_deletes_existing_branch_when_confirmed(self, monkeypatch):
        monkeypatch.setattr(bv, "_branch_exists", lambda _branch: True)
        monkeypatch.setattr(bv, "_confirm_branch_overwrite", lambda _branch: True)
        monkeypatch.setattr(bv, "_current_branch", lambda: "main")
        calls: list[list[str]] = []

        def _fake_run(cmd: list[str], *, dry_run: bool, label: str) -> None:
            assert dry_run is False
            assert label
            calls.append(cmd)

        monkeypatch.setattr(bv, "_run", _fake_run)
        bv._prepare_release_branch("release/v1.2.3", base="main", dry_run=False)
        assert calls == [["git", "branch", "-D", "release/v1.2.3"]]

    def test_checks_out_base_before_delete_if_branch_is_current(self, monkeypatch):
        monkeypatch.setattr(bv, "_branch_exists", lambda _branch: True)
        monkeypatch.setattr(bv, "_confirm_branch_overwrite", lambda _branch: True)
        monkeypatch.setattr(bv, "_current_branch", lambda: "release/v1.2.3")
        calls: list[list[str]] = []

        def _fake_run(cmd: list[str], *, dry_run: bool, label: str) -> None:
            assert dry_run is False
            assert label
            calls.append(cmd)

        monkeypatch.setattr(bv, "_run", _fake_run)
        bv._prepare_release_branch("release/v1.2.3", base="main", dry_run=False)
        assert calls == [
            ["git", "checkout", "main"],
            ["git", "branch", "-D", "release/v1.2.3"],
        ]

    def test_aborts_when_current_and_base_are_same_release_branch(self, monkeypatch):
        monkeypatch.setattr(bv, "_branch_exists", lambda _branch: True)
        monkeypatch.setattr(bv, "_confirm_branch_overwrite", lambda _branch: True)
        monkeypatch.setattr(bv, "_current_branch", lambda: "release/v1.2.3")
        with pytest.raises(SystemExit, match="1"):
            bv._prepare_release_branch(
                "release/v1.2.3",
                base="release/v1.2.3",
                dry_run=False,
            )
