"""Shared CI YAML utilities for GitHub Actions and GitLab CI analyzers."""

from __future__ import annotations

from typing import Any

import yaml


def load_ci_yaml(code: str) -> dict[str, Any]:
    """Parse YAML text into a mapping, returning an empty dict on parse failure."""
    try:
        parsed = yaml.safe_load(code)
    except yaml.YAMLError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def workflow_jobs(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return the jobs mapping from a CI workflow document."""
    jobs = document.get("jobs")
    if not isinstance(jobs, dict):
        return {}
    return {name: value for name, value in jobs.items() if isinstance(value, dict)}


def job_steps(job: dict[str, Any]) -> list[dict[str, Any]]:
    """Return normalized step mappings for a single CI job."""
    steps = job.get("steps")
    if not isinstance(steps, list):
        return []
    return [step for step in steps if isinstance(step, dict)]
