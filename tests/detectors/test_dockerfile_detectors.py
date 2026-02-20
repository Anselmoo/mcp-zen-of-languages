from __future__ import annotations

from mcp_zen_of_languages.analyzers.base import AnalysisContext
from mcp_zen_of_languages.languages.configs import (
    DockerfileAddInstructionConfig,
    DockerfileDockerignoreConfig,
    DockerfileHealthcheckConfig,
    DockerfileLatestTagConfig,
    DockerfileLayerDisciplineConfig,
    DockerfileMultiStageConfig,
    DockerfileNonRootUserConfig,
    DockerfileSecretHygieneConfig,
)
from mcp_zen_of_languages.languages.dockerfile.detectors import (
    DockerfileAddInstructionDetector,
    DockerfileDockerignoreDetector,
    DockerfileHealthcheckDetector,
    DockerfileLatestTagDetector,
    DockerfileLayerDisciplineDetector,
    DockerfileMultiStageDetector,
    DockerfileNonRootUserDetector,
    DockerfileSecretHygieneDetector,
)


def test_dockerfile_detectors_emit_expected_violations():
    code = """FROM ubuntu:latest
ADD ./app /app
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*
RUN echo done
RUN echo done-again
ARG API_KEY=abc
USER root
"""
    context = AnalysisContext(code=code, language="dockerfile")

    assert DockerfileLatestTagDetector().detect(context, DockerfileLatestTagConfig())
    assert DockerfileNonRootUserDetector().detect(
        context, DockerfileNonRootUserConfig()
    )
    assert DockerfileAddInstructionDetector().detect(
        context,
        DockerfileAddInstructionConfig(),
    )
    assert DockerfileHealthcheckDetector().detect(
        context, DockerfileHealthcheckConfig()
    )
    assert DockerfileSecretHygieneDetector().detect(
        context,
        DockerfileSecretHygieneConfig(),
    )
    assert DockerfileLayerDisciplineDetector().detect(
        context,
        DockerfileLayerDisciplineConfig(max_run_instructions=3),
    )


def test_dockerfile_multistage_detector_flags_compiled_single_stage():
    context = AnalysisContext(
        code="FROM golang:1.22\nRUN go build ./...\n",
        language="dockerfile",
    )
    violations = DockerfileMultiStageDetector().detect(
        context,
        DockerfileMultiStageConfig(),
    )
    assert violations


def test_dockerfile_dockerignore_detector_checks_other_files():
    context = AnalysisContext(
        code="FROM alpine:3.20\nCOPY . /app\n",
        language="dockerfile",
        other_files={"Dockerfile": "FROM alpine:3.20\nCOPY . /app\n"},
    )
    violations = DockerfileDockerignoreDetector().detect(
        context,
        DockerfileDockerignoreConfig(),
    )
    assert violations


def test_dockerfile_detectors_cover_non_violation_paths_and_names():
    clean_context = AnalysisContext(
        code=(
            "FROM golang:1.22 AS build\n"
            "RUN go build ./...\n"
            "FROM gcr.io/distroless/base-debian12\n"
            "USER app\n"
            "HEALTHCHECK CMD /bin/true\n"
        ),
        language="dockerfile",
    )
    assert DockerfileLatestTagDetector().name == "dockerfile-001"
    assert DockerfileNonRootUserDetector().name == "dockerfile-002"
    assert DockerfileAddInstructionDetector().name == "dockerfile-003"
    assert DockerfileHealthcheckDetector().name == "dockerfile-004"
    assert DockerfileMultiStageDetector().name == "dockerfile-005"
    assert DockerfileSecretHygieneDetector().name == "dockerfile-006"
    assert DockerfileLayerDisciplineDetector().name == "dockerfile-007"
    assert DockerfileDockerignoreDetector().name == "dockerfile-008"
    assert not DockerfileNonRootUserDetector().detect(
        clean_context,
        DockerfileNonRootUserConfig(),
    )
    assert not DockerfileHealthcheckDetector().detect(
        clean_context,
        DockerfileHealthcheckConfig(),
    )
    assert not DockerfileMultiStageDetector().detect(
        clean_context,
        DockerfileMultiStageConfig(),
    )

    no_user_context = AnalysisContext(code="FROM alpine:3.20\n", language="dockerfile")
    assert DockerfileNonRootUserDetector().detect(
        no_user_context,
        DockerfileNonRootUserConfig(),
    )

    no_copy_context = AnalysisContext(
        code="FROM alpine:3.20\nRUN echo ok\n",
        language="dockerfile",
    )
    assert not DockerfileDockerignoreDetector().detect(
        no_copy_context,
        DockerfileDockerignoreConfig(),
    )

    copy_context_without_other_files = AnalysisContext(
        code="FROM alpine:3.20\nCOPY . /app\n",
        language="dockerfile",
    )
    assert not DockerfileDockerignoreDetector().detect(
        copy_context_without_other_files,
        DockerfileDockerignoreConfig(),
    )

    copy_context_with_dockerignore = AnalysisContext(
        code="FROM alpine:3.20\nCOPY . /app\n",
        language="dockerfile",
        other_files={".dockerignore": "__pycache__/\n"},
    )
    assert not DockerfileDockerignoreDetector().detect(
        copy_context_with_dockerignore,
        DockerfileDockerignoreConfig(),
    )
