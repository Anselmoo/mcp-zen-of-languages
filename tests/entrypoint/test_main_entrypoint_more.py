from __future__ import annotations

import runpy

from mcp_zen_of_languages import __main__


def test_main_entrypoint_callable():
    assert callable(__main__.main)


def test_main_entrypoint_dunder_main(monkeypatch):
    monkeypatch.setattr(__main__.mcp, "run", lambda: None)
    runpy.run_module("mcp_zen_of_languages.__main__", run_name="__main__")
