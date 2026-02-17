from __future__ import annotations

from mcp_zen_of_languages import __main__


def test_main_entrypoint_runs(monkeypatch):
    called = {}

    def fake_run():
        called["run"] = True

    monkeypatch.setattr(__main__.mcp, "run", fake_run)
    __main__.main()
    assert called["run"] is True
