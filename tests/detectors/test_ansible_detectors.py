from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.ansible.analyzer import AnsibleAnalyzer
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleBecomeDetector
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleFqcnDetector
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleIdempotencyDetector
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleJinjaSpacingDetector
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleNamingDetector
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleNoCleartextPasswordDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleStateExplicitDetector,
)
from mcp_zen_of_languages.languages.configs import AnsibleBecomeConfig
from mcp_zen_of_languages.languages.configs import AnsibleFqcnConfig
from mcp_zen_of_languages.languages.configs import AnsibleIdempotencyConfig
from mcp_zen_of_languages.languages.configs import AnsibleJinjaSpacingConfig
from mcp_zen_of_languages.languages.configs import AnsibleNamingConfig
from mcp_zen_of_languages.languages.configs import AnsibleNoCleartextPasswordConfig
from mcp_zen_of_languages.languages.configs import AnsibleStateExplicitConfig


def _context(code: str) -> AnalysisContext:
    ast_tree = AnsibleAnalyzer().parse_code(code)
    return AnalysisContext(code=code, language="ansible", ast_tree=ast_tree)


def test_ansible_detectors_emit_expected_violations():
    code = (
        "- hosts: all\n"
        "  sudo: yes\n"
        "  tasks:\n"
        "    - shell: mkdir -p /tmp/demo\n"
        "      password: secret123\n"
        "    - apt:\n"
        "        name: nginx\n"
        "    - debug:\n"
        '        msg: "{{bad_var}}"\n'
    )
    context = _context(code)
    assert AnsibleNamingDetector().detect(context, AnsibleNamingConfig())
    assert AnsibleFqcnDetector().detect(context, AnsibleFqcnConfig())
    assert AnsibleIdempotencyDetector().detect(context, AnsibleIdempotencyConfig())
    assert AnsibleBecomeDetector().detect(context, AnsibleBecomeConfig())
    assert AnsibleStateExplicitDetector().detect(context, AnsibleStateExplicitConfig())
    assert AnsibleNoCleartextPasswordDetector().detect(
        context, AnsibleNoCleartextPasswordConfig()
    )
    assert AnsibleJinjaSpacingDetector().detect(context, AnsibleJinjaSpacingConfig())


def test_ansible_detectors_cover_clean_paths():
    code = (
        "- name: Configure host\n"
        "  hosts: all\n"
        "  become: true\n"
        "  tasks:\n"
        "    - name: Install nginx package\n"
        "      ansible.builtin.package:\n"
        "        name: nginx\n"
        "        state: present\n"
        "    - name: Show message\n"
        "      ansible.builtin.debug:\n"
        '        msg: "{{ app_name }}"\n'
    )
    context = _context(code)
    assert AnsibleNamingDetector().name == "ansible-001"
    assert AnsibleFqcnDetector().name == "ansible-002"
    assert AnsibleIdempotencyDetector().name == "ansible-003"
    assert AnsibleBecomeDetector().name == "ansible-004"
    assert AnsibleStateExplicitDetector().name == "ansible-005"
    assert AnsibleNoCleartextPasswordDetector().name == "ansible-006"
    assert AnsibleJinjaSpacingDetector().name == "ansible-007"
    assert not AnsibleNamingDetector().detect(context, AnsibleNamingConfig())
    assert not AnsibleFqcnDetector().detect(context, AnsibleFqcnConfig())
    assert not AnsibleIdempotencyDetector().detect(context, AnsibleIdempotencyConfig())
    assert not AnsibleBecomeDetector().detect(context, AnsibleBecomeConfig())
    assert not AnsibleStateExplicitDetector().detect(
        context, AnsibleStateExplicitConfig()
    )
    assert not AnsibleNoCleartextPasswordDetector().detect(
        context, AnsibleNoCleartextPasswordConfig()
    )
    assert not AnsibleJinjaSpacingDetector().detect(
        context, AnsibleJinjaSpacingConfig()
    )
