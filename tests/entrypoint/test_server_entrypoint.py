from __future__ import annotations

from mcp_zen_of_languages import server


def test_server_entrypoint_callable() -> None:
    assert callable(server.main)


def test_server_entrypoint_runs(monkeypatch) -> None:
    called = {}

    def fake_run() -> None:
        called["run"] = True

    monkeypatch.setattr(server.mcp, "run", fake_run)
    server.main()
    assert called["run"] is True
