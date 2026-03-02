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


def test_ansible_detectors_support_root_task_list_documents():
    context = _context(
        "- shell: mkdir -p /tmp/demo\n  password: cleartext\n- apt:\n    name: nginx\n"
    )
    assert AnsibleNamingDetector().detect(context, AnsibleNamingConfig())
    assert AnsibleIdempotencyDetector().detect(context, AnsibleIdempotencyConfig())
    assert AnsibleStateExplicitDetector().detect(context, AnsibleStateExplicitConfig())


def test_ansible_detectors_handle_action_and_local_action_module_forms():
    context = _context(
        "- hosts: all\n"
        "  tasks:\n"
        "    - name: create directory\n"
        "      action:\n"
        "        module: ansible.builtin.file\n"
        "        path: /tmp/demo\n"
        "        state: directory\n"
        "    - name: create local directory\n"
        "      local_action: ansible.builtin.file path=/tmp/local state=directory\n"
    )
    assert not AnsibleFqcnDetector().detect(context, AnsibleFqcnConfig())
    assert not AnsibleStateExplicitDetector().detect(
        context, AnsibleStateExplicitConfig()
    )


def test_ansible_detector_locations_track_repeated_module_lines():
    context = _context(
        "- hosts: all\n  tasks:\n    - shell: echo one\n    - shell: echo two\n"
    )
    naming = AnsibleNamingDetector().detect(context, AnsibleNamingConfig())
    idempotency = AnsibleIdempotencyDetector().detect(
        context, AnsibleIdempotencyConfig()
    )
    assert [violation.location.line for violation in naming] == [1, 3, 4]
    assert [violation.location.line for violation in idempotency] == [3, 4]


def test_ansible_state_detector_accepts_string_form_state_argument():
    context = _context(
        "- hosts: all\n"
        "  tasks:\n"
        "    - name: install nginx\n"
        "      apt: name=nginx state=present\n"
    )
    assert not AnsibleStateExplicitDetector().detect(
        context, AnsibleStateExplicitConfig()
    )
