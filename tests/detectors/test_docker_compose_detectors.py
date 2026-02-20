from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.configs import (
    DockerComposeHealthcheckConfig,
    DockerComposeLatestTagConfig,
    DockerComposeNonRootUserConfig,
    DockerComposeSecretHygieneConfig,
)
from mcp_zen_of_languages.languages.docker_compose.detectors import (
    DockerComposeHealthcheckDetector,
    DockerComposeLatestTagDetector,
    DockerComposeNonRootUserDetector,
    DockerComposeSecretHygieneDetector,
)


def test_docker_compose_detectors_emit_expected_violations():
    context = AnalysisContext(
        code=(
            "services:\n"
            "  web:\n"
            "    image: nginx:latest\n"
            "    user: root\n"
            "    environment:\n"
            "      API_KEY: hardcoded\n"
        ),
        language="docker_compose",
    )
    assert DockerComposeLatestTagDetector().detect(
        context,
        DockerComposeLatestTagConfig(),
    )
    assert DockerComposeNonRootUserDetector().detect(
        context,
        DockerComposeNonRootUserConfig(),
    )
    assert DockerComposeHealthcheckDetector().detect(
        context,
        DockerComposeHealthcheckConfig(),
    )
    assert DockerComposeSecretHygieneDetector().detect(
        context,
        DockerComposeSecretHygieneConfig(),
    )


def test_docker_compose_detectors_cover_clean_paths():
    context = AnalysisContext(
        code=(
            "services:\n"
            "  web:\n"
            "    image: nginx:1.27.2\n"
            "    user: 1000:1000\n"
            "    healthcheck:\n"
            "      test: ['CMD', 'curl', '-f', 'http://localhost']\n"
            "    environment:\n"
            "      APP_MODE: production\n"
        ),
        language="docker_compose",
    )
    assert DockerComposeLatestTagDetector().name == "docker-compose-001"
    assert DockerComposeNonRootUserDetector().name == "docker-compose-002"
    assert DockerComposeHealthcheckDetector().name == "docker-compose-003"
    assert DockerComposeSecretHygieneDetector().name == "docker-compose-004"
    assert not DockerComposeLatestTagDetector().detect(
        context,
        DockerComposeLatestTagConfig(),
    )
    assert not DockerComposeNonRootUserDetector().detect(
        context,
        DockerComposeNonRootUserConfig(),
    )
    assert not DockerComposeHealthcheckDetector().detect(
        context,
        DockerComposeHealthcheckConfig(),
    )
    assert not DockerComposeSecretHygieneDetector().detect(
        context,
        DockerComposeSecretHygieneConfig(),
    )
