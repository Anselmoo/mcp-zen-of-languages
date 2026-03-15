from __future__ import annotations

from mcp_zen_of_languages.analyzers.analyzer_factory import create_analyzer
from mcp_zen_of_languages.languages.ci_yaml_utils import job_steps
from mcp_zen_of_languages.languages.ci_yaml_utils import load_ci_yaml
from mcp_zen_of_languages.languages.ci_yaml_utils import workflow_jobs


def test_github_actions_detector_finds_security_and_timeout_issues():
    code = """name: CI
on: pull_request_target
jobs:
      build:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
            with:
              ref: ${{ github.event.pull_request.head.sha }}
          - run: echo "${{ secrets.MY_SECRET }}"
    """
    result = create_analyzer("github-actions").analyze(code)
    rule_ids = {violation.rule_id for violation in result.violations}
    principles = {violation.principle for violation in result.violations}
    assert {"gha-001", "gha-002", "gha-003", "gha-008"} <= rule_ids
    assert "Pin third-party actions by full commit SHA" in principles
    assert "Avoid pull_request_target checkout of untrusted head SHA" in principles
    assert "Do not expose secrets in run blocks" in principles
    assert "Set timeout-minutes on jobs" in principles


def test_github_actions_detector_finds_deprecated_and_artifact_issues():
    code = """name: Build
on: push
permissions: read-all
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    permissions:
      contents: read
    steps:
      - run: echo "::set-output name=foo::bar"
        shell: bash
      - uses: actions/upload-artifact@v4
        with:
          name: build
    """
    result = create_analyzer("github-actions").analyze(code)
    rule_ids = {violation.rule_id for violation in result.violations}
    principles = {violation.principle for violation in result.violations}
    assert {"gha-011", "gha-015"} <= rule_ids
    assert "Use GITHUB_OUTPUT instead of deprecated set-output" in principles
    assert "Set artifact retention explicitly" in principles


def test_ci_yaml_utils_handle_invalid_or_unexpected_shapes():
    assert load_ci_yaml(": bad: yaml:") == {}
    assert workflow_jobs({"jobs": []}) == {}
    assert job_steps({"steps": {}}) == []
