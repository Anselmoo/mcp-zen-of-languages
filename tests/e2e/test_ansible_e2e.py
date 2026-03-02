from __future__ import annotations

from mcp_zen_of_languages.analyzers.analyzer_factory import create_analyzer


def test_ansible_analyze_end_to_end():
    result = create_analyzer("ansible").analyze(
        "- hosts: all\n"
        "  tasks:\n"
        "    - shell: mkdir -p /tmp/demo\n"
        "    - debug:\n"
        '        msg: "{{bad_var}}"\n',
        path="playbook.yml",
    )
    assert result.language == "ansible"
    assert result.violations
