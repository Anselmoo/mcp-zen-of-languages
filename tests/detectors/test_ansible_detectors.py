from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.ansible.analyzer import AnsibleAnalyzer
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleAutomationJourneyDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleAutomationOpportunityDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleBecomeDetector
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleComplexityProductivityDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleContinuousImprovementDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleConventionOverConfigDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleDeclarativeBiasDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleExplainabilityDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleFocusDetector
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleFqcnDetector
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleFrictionDetector
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleIdempotencyDetector
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleJinjaSpacingDetector
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleMagicAutomationDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleNamingDetector
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleNoCleartextPasswordDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleReadabilityCountsDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleStateExplicitDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import (
    AnsibleUserExperienceDetector,
)
from mcp_zen_of_languages.languages.ansible.detectors import AnsibleUserOutcomeDetector
from mcp_zen_of_languages.languages.configs import AnsibleAutomationJourneyConfig
from mcp_zen_of_languages.languages.configs import AnsibleAutomationOpportunityConfig
from mcp_zen_of_languages.languages.configs import AnsibleBecomeConfig
from mcp_zen_of_languages.languages.configs import (
    AnsibleComplexityKillsProductivityConfig,
)
from mcp_zen_of_languages.languages.configs import AnsibleContinuousImprovementConfig
from mcp_zen_of_languages.languages.configs import AnsibleConventionOverConfigConfig
from mcp_zen_of_languages.languages.configs import AnsibleDeclarativeBiasConfig
from mcp_zen_of_languages.languages.configs import AnsibleExplainabilityConfig
from mcp_zen_of_languages.languages.configs import AnsibleFocusConfig
from mcp_zen_of_languages.languages.configs import AnsibleFqcnConfig
from mcp_zen_of_languages.languages.configs import AnsibleFrictionConfig
from mcp_zen_of_languages.languages.configs import AnsibleIdempotencyConfig
from mcp_zen_of_languages.languages.configs import AnsibleJinjaSpacingConfig
from mcp_zen_of_languages.languages.configs import AnsibleMagicAutomationConfig
from mcp_zen_of_languages.languages.configs import AnsibleNamingConfig
from mcp_zen_of_languages.languages.configs import AnsibleNoCleartextPasswordConfig
from mcp_zen_of_languages.languages.configs import AnsibleReadabilityCountsConfig
from mcp_zen_of_languages.languages.configs import AnsibleStateExplicitConfig
from mcp_zen_of_languages.languages.configs import AnsibleUserExperienceConfig
from mcp_zen_of_languages.languages.configs import AnsibleUserOutcomeConfig


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


def test_ansible_zen_008_020_detectors_emit_expected_violations():
    code = (
        "- hosts: all\n"
        "  tasks:\n"
        "    - shell: python3 -c 'print(1)'\n"
        "      ignore_errors: true\n"
        "      when: a and b and c and d\n"
        "    - raw: uname -a\n"
        "    - shell: apt-get install -y nginx\n"
        "    - shell: echo repeat\n"
        "    - shell: echo repeat\n"
        "    - command: "
        "echo this-inline-command-is-very-long-and-hard-to-explain-"
        "because-it-keeps-growing-with-flags-and-arguments-and-more\n"
        "    - pause:\n"
        "    - debug:\n"
        '        msg: "{{ too_dense }}"\n'
        "# TODO improve this automation path\n"
    )
    context = _context(code)
    assert AnsibleReadabilityCountsDetector().detect(
        context, AnsibleReadabilityCountsConfig()
    )
    assert AnsibleUserOutcomeDetector().detect(context, AnsibleUserOutcomeConfig())
    assert AnsibleUserExperienceDetector().detect(
        context, AnsibleUserExperienceConfig()
    )
    assert AnsibleMagicAutomationDetector().detect(
        context, AnsibleMagicAutomationConfig()
    )
    assert AnsibleConventionOverConfigDetector().detect(
        context, AnsibleConventionOverConfigConfig()
    )
    assert AnsibleDeclarativeBiasDetector().detect(
        context, AnsibleDeclarativeBiasConfig()
    )
    assert AnsibleFocusDetector().detect(
        context, AnsibleFocusConfig(max_tasks_per_play=2)
    )
    assert AnsibleComplexityProductivityDetector().detect(
        context, AnsibleComplexityKillsProductivityConfig(max_condition_operators=1)
    )
    assert AnsibleExplainabilityDetector().detect(
        context, AnsibleExplainabilityConfig(max_inline_command_length=40)
    )
    assert AnsibleAutomationOpportunityDetector().detect(
        context, AnsibleAutomationOpportunityConfig(min_repeated_shell_commands=2)
    )
    assert AnsibleContinuousImprovementDetector().detect(
        context, AnsibleContinuousImprovementConfig()
    )
    assert AnsibleFrictionDetector().detect(context, AnsibleFrictionConfig())
    assert AnsibleAutomationJourneyDetector().detect(
        context, AnsibleAutomationJourneyConfig()
    )


def test_ansible_zen_008_020_detectors_cover_clean_paths():
    code = (
        "- name: healthy play\n"
        "  hosts: all\n"
        "  tasks:\n"
        "    - name: install package declaratively\n"
        "      tags: [lifecycle]\n"
        "      ansible.builtin.package:\n"
        "        name: nginx\n"
        "        state: present\n"
        "    - name: show output\n"
        "      tags: [lifecycle]\n"
        "      ansible.builtin.debug:\n"
        '        msg: "all good"\n'
    )
    context = _context(code)
    assert not AnsibleReadabilityCountsDetector().detect(
        context, AnsibleReadabilityCountsConfig()
    )
    assert not AnsibleUserOutcomeDetector().detect(context, AnsibleUserOutcomeConfig())
    assert not AnsibleUserExperienceDetector().detect(
        context, AnsibleUserExperienceConfig()
    )
    assert not AnsibleMagicAutomationDetector().detect(
        context, AnsibleMagicAutomationConfig()
    )
    assert not AnsibleConventionOverConfigDetector().detect(
        context, AnsibleConventionOverConfigConfig()
    )
    assert not AnsibleDeclarativeBiasDetector().detect(
        context, AnsibleDeclarativeBiasConfig()
    )
    assert not AnsibleFocusDetector().detect(
        context, AnsibleFocusConfig(max_tasks_per_play=10)
    )
    assert not AnsibleComplexityProductivityDetector().detect(
        context, AnsibleComplexityKillsProductivityConfig(max_condition_operators=2)
    )
    assert not AnsibleExplainabilityDetector().detect(
        context, AnsibleExplainabilityConfig(max_inline_command_length=140)
    )
    assert not AnsibleAutomationOpportunityDetector().detect(
        context, AnsibleAutomationOpportunityConfig(min_repeated_shell_commands=2)
    )
    assert not AnsibleContinuousImprovementDetector().detect(
        context, AnsibleContinuousImprovementConfig()
    )
    assert not AnsibleFrictionDetector().detect(context, AnsibleFrictionConfig())
    assert not AnsibleAutomationJourneyDetector().detect(
        context, AnsibleAutomationJourneyConfig()
    )


def test_ansible_magic_automation_reports_matching_shell_line():
    expected_line = 6
    context = _context(
        "- hosts: all\n"
        "  tasks:\n"
        "    - name: harmless shell\n"
        "      shell: echo hello\n"
        "    - name: manual package install\n"
        "      shell: apt-get install -y nginx\n"
    )
    violations = AnsibleMagicAutomationDetector().detect(
        context, AnsibleMagicAutomationConfig()
    )
    assert len(violations) == 1
    assert violations[0].location is not None
    assert violations[0].location.line == expected_line


def test_ansible_explainability_reports_long_command_line():
    expected_line = 6
    context = _context(
        "- hosts: all\n"
        "  tasks:\n"
        "    - name: short command\n"
        "      command: echo short\n"
        "    - name: long command\n"
        "      command: "
        "echo this-inline-command-is-very-long-and-hard-to-explain-"
        "because-it-keeps-growing-with-flags-and-arguments-and-more\n"
    )
    violations = AnsibleExplainabilityDetector().detect(
        context, AnsibleExplainabilityConfig(max_inline_command_length=40)
    )
    assert len(violations) == 1
    assert violations[0].location is not None
    assert violations[0].location.line == expected_line


def test_ansible_focus_reports_oversized_second_play_line():
    expected_line = 9
    context = _context(
        "- name: first\n"
        "  hosts: all\n"
        "  tasks:\n"
        "    - name: only task\n"
        "      ansible.builtin.debug:\n"
        '        msg: "ok"\n'
        "- name: second\n"
        "  hosts: all\n"
        "  tasks:\n"
        "    - name: one\n"
        "      ansible.builtin.debug:\n"
        '        msg: "one"\n'
        "    - name: two\n"
        "      ansible.builtin.debug:\n"
        '        msg: "two"\n'
    )
    violations = AnsibleFocusDetector().detect(
        context, AnsibleFocusConfig(max_tasks_per_play=1)
    )
    assert len(violations) == 1
    assert violations[0].location is not None
    assert violations[0].location.line == expected_line
