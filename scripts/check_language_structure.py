from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

REQUIRED_FILES = {
    "__init__.py",
    "analyzer.py",
    "detectors.py",
    "mapping.py",
    "rules.py",
}
LEGACY_MARKERS = ("legacy", "deprecated")


def _parse_all(detectors_path: Path) -> list[str] | None:
    module = ast.parse(detectors_path.read_text(encoding="utf-8"))
    for node in module.body:
        if isinstance(node, ast.Assign):
            if not any(
                isinstance(target, ast.Name) and target.id == "__all__"
                for target in node.targets
            ):
                continue
            value = ast.literal_eval(node.value)
            if isinstance(value, (list, tuple)) and all(
                isinstance(item, str) for item in value
            ):
                return list(value)
            return None
    return None


def _check_legacy_files(root: Path, label: str, errors: list[str]) -> None:
    for path in root.rglob("*.py"):
        lower_name = path.name.lower()
        if any(marker in lower_name for marker in LEGACY_MARKERS):
            errors.append(f"{label}: legacy marker in {path.name}")


def _unexpected_python_modules(language_dir: Path) -> list[str]:
    return sorted(
        path.name
        for path in language_dir.iterdir()
        if path.is_file()
        and path.suffix == ".py"
        and path.name not in REQUIRED_FILES
    )


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root / "src"))

    errors: list[str] = []
    languages_root = repo_root / "src" / "mcp_zen_of_languages" / "languages"
    detectors_root = repo_root / "src" / "mcp_zen_of_languages" / "detectors"
    metrics_root = repo_root / "src" / "mcp_zen_of_languages" / "metrics"
    analyzers_root = repo_root / "src" / "mcp_zen_of_languages" / "analyzers"

    if not languages_root.exists():
        print(f"Languages directory not found: {languages_root}")
        return 1

    if detectors_root.exists():
        errors.append("detectors package should be removed")

    _check_legacy_files(metrics_root, "metrics", errors)
    _check_legacy_files(analyzers_root, "analyzers", errors)

    from mcp_zen_of_languages.analyzers import registry_bootstrap  # noqa: F401
    from mcp_zen_of_languages.analyzers.registry import REGISTRY
    from mcp_zen_of_languages.rules import get_all_languages, get_language_zen
    from mcp_zen_of_languages.rules.base_models import get_rule_id_coverage
    from mcp_zen_of_languages.utils.language_detection import EXTENSION_LANGUAGE_MAP

    languages = set(get_all_languages())
    for ext, lang in EXTENSION_LANGUAGE_MAP.items():
        if not ext.startswith("."):
            errors.append(f"extension mapping missing dot prefix: {ext}")
        if lang not in languages:
            errors.append(f"extension mapping references unknown language: {lang}")

    for entry in sorted(languages_root.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("__"):
            continue
        if entry.name != entry.name.lower():
            errors.append(f"{entry.name}: folder name must be lowercase")
        if entry.name not in languages:
            errors.append(f"{entry.name}: no rules registry entry")
            continue
        if missing := sorted(REQUIRED_FILES - {p.name for p in entry.iterdir()}):
            errors.append(f"{entry.name}: missing {', '.join(missing)}")
            continue
        if unexpected_modules := _unexpected_python_modules(entry):
            errors.append(
                f"{entry.name}: unexpected python modules {unexpected_modules}"
            )
            continue
        mapping_module_name = f"mcp_zen_of_languages.languages.{entry.name}.mapping"
        try:
            mapping_module = importlib.import_module(mapping_module_name)
        except ModuleNotFoundError as exc:
            if exc.name == mapping_module_name:
                errors.append(f"{entry.name}: mapping.py module not found")
                continue
            raise
        detector_map = getattr(mapping_module, "DETECTOR_MAP", None)
        if detector_map is None:
            errors.append(f"{entry.name}: DETECTOR_MAP missing from mapping.py")
            continue
        if detector_map.language != entry.name:
            errors.append(
                f"{entry.name}: DETECTOR_MAP language mismatch {detector_map.language}"
            )
            continue
        detectors_path = entry / "detectors.py"
        exported = _parse_all(detectors_path)
        if exported is None:
            errors.append(f"{entry.name}: __all__ must be a list of strings")
            continue
        registry_detectors = {
            meta.detector_class.__name__
            for meta in REGISTRY.items()
            if meta.language == entry.name
        }
        missing_exports = sorted(registry_detectors - set(exported))
        extra_exports = sorted(set(exported) - registry_detectors)
        if missing_exports or extra_exports:
            errors.append(
                f"{entry.name}: __all__ mismatch missing={missing_exports} extra={extra_exports}"
            )
        lang_zen = get_language_zen(entry.name)
        if lang_zen is None:
            errors.append(f"{entry.name}: missing rules definition")
            continue
        missing_rule_ids, unknown_rule_ids = get_rule_id_coverage(lang_zen)
        if missing_rule_ids or unknown_rule_ids:
            errors.append(
                f"{entry.name}: rule_id gaps missing={missing_rule_ids} unknown={unknown_rule_ids}"
            )
        rule_ids = {principle.id for principle in lang_zen.principles}
        rule_map_keys: set[str] = set()
        for meta in REGISTRY.items():
            if meta.language != entry.name:
                continue
            rule_map_keys.update(meta.rule_map.keys())
        if unknown_rule_keys := sorted(rule_map_keys - rule_ids):
            errors.append(
                f"{entry.name}: rule_map references unknown rules {unknown_rule_keys}"
            )
        for principle in lang_zen.principles:
            specs = principle.violation_specs
            all_violation_ids = {spec.id for spec in specs}
            required_ids = {
                spec.id
                for spec in specs
                if not spec.id.startswith(("manual-", "todo-"))
            }
            if not required_ids:
                continue
            covered: set[str] = set()
            full_coverage = False
            unknown_specs: set[str] = set()
            for meta in REGISTRY.items():
                if meta.language != entry.name:
                    continue
                coverage = meta.rule_map.get(principle.id, [])
                if "*" in coverage:
                    full_coverage = True
                    break
                coverage_set = set(coverage)
                covered.update(coverage_set)
                unknown_specs.update(coverage_set - all_violation_ids)
            if unknown_specs:
                errors.append(
                    f"{entry.name}: {principle.id} unknown violation ids {sorted(unknown_specs)}"
                )
            if full_coverage:
                continue
            if missing_specs := sorted(required_ids - covered):
                errors.append(
                    f"{entry.name}: {principle.id} missing violations {missing_specs}"
                )

    if errors:
        print("Language module validation failures found:")
        for error in errors:
            print(f" - {error}")
        return 1

    print("Language module validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
