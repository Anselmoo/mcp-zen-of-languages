from __future__ import annotations

from mcp_zen_of_languages.analyzers.analyzer_factory import create_analyzer
from mcp_zen_of_languages.languages.gitlab_ci.detectors import (
    AllowFailureWithoutRulesDetector,
    ArtifactExpiryDetector,
    DuplicatedBeforeScriptDetector,
    ExposedVariablesDetector,
    GodPipelineDetector,
    MissingCacheKeyDetector,
    MissingInterruptibleDetector,
    MissingNeedsDetector,
    OnlyExceptDetector,
    UnpinnedImageTagDetector,
)

DETECTOR_CLASS_COUNT = 10
EXPECTED_EXPOSED_VARIABLES_COUNT = 2
EXPECTED_DUPLICATED_BEFORE_SCRIPT_COUNT = 2


def test_gitlab_ci_detector_classes_are_available():
    detector_classes = {
        AllowFailureWithoutRulesDetector,
        ArtifactExpiryDetector,
        DuplicatedBeforeScriptDetector,
        ExposedVariablesDetector,
        GodPipelineDetector,
        MissingCacheKeyDetector,
        MissingInterruptibleDetector,
        MissingNeedsDetector,
        OnlyExceptDetector,
        UnpinnedImageTagDetector,
    }
    assert len(detector_classes) == DETECTOR_CLASS_COUNT


def test_gitlab_ci_detects_security_and_idiomatic_issues():
    analyzer = create_analyzer("gitlab-ci")
    code = """
variables:
  CI_SECRET_TOKEN: "hardcoded"

build:
  image: python
  allow_failure: true
  only:
    - merge_requests
  script:
    - pip install -r requirements.txt
"""
    result = analyzer.analyze(code)
    principles = {violation.principle for violation in result.violations}
    assert "Pin container image tags" in principles
    assert "Avoid exposed variables in repository YAML" in principles
    assert "Use allow_failure only with rules-based context" in principles
    assert "Prefer rules over only/except" in principles
    assert "Cache dependency installs" in principles


def test_gitlab_ci_detects_artifacts_without_expiry():
    analyzer = create_analyzer("gitlab-ci")
    code = """
build:
  script:
    - echo hello
  artifacts:
    paths:
      - dist/
"""
    result = analyzer.analyze(code)
    principles = {violation.principle for violation in result.violations}
    assert "Expire artifacts" in principles


def test_gitlab_ci_detects_parallel_job_without_needs():
    analyzer = create_analyzer("gitlab-ci")
    code = """
test:
  parallel: 3
  script:
    - echo test
"""
    result = analyzer.analyze(code)
    principles = {violation.principle for violation in result.violations}
    assert "Model job DAG dependencies with needs" in principles


def test_gitlab_ci_only_except_in_comments_are_ignored():
    analyzer = create_analyzer("gitlab-ci")
    code = """
# only:
#   - merge_requests
# except:
#   - tags
build:
  script:
    - echo "comment mention only"
"""
    result = analyzer.analyze(code)
    principles = {violation.principle for violation in result.violations}
    assert "Prefer rules over only/except" not in principles


def test_gitlab_ci_exposed_variables_reports_multiple_matches():
    analyzer = create_analyzer("gitlab-ci")
    code = """
variables:
  API_TOKEN: "a"
  DB_PASSWORD: "b"
build:
  script:
    - echo ok
"""
    result = analyzer.analyze(code)
    exposed = [
        violation
        for violation in result.violations
        if violation.principle == "Avoid exposed variables in repository YAML"
    ]
    assert len(exposed) == EXPECTED_EXPOSED_VARIABLES_COUNT


def test_gitlab_ci_duplicated_before_script_reports_multiple_jobs():
    analyzer = create_analyzer("gitlab-ci")
    code = """
job_one:
  before_script:
    - echo "prepare"
  script:
    - echo one

job_two:
  before_script:
    - echo "prepare"
  script:
    - echo two

job_three:
   before_script:
     - echo "prepare"
   script:
     - echo three
"""
    result = analyzer.analyze(code)
    duplicates = [
        violation
        for violation in result.violations
        if violation.principle == "Reduce duplicated before_script blocks"
    ]
    assert len(duplicates) == EXPECTED_DUPLICATED_BEFORE_SCRIPT_COUNT


def test_gitlab_ci_missing_interruptible_ignored_for_non_mr_jobs():
    analyzer = create_analyzer("gitlab-ci")
    code = """
nightly_tests:
  only:
    - schedules
  script:
    - echo "nightly tests"
"""
    result = analyzer.analyze(code)
    principles = {violation.principle for violation in result.violations}
    assert "Use interruptible pipelines" not in principles
