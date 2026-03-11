"""Validate that dogma ID usage is consistent across language mappings.

Rules:

- Production language ``mapping.py`` files: ``FULL_DOGMA_IDS`` must be a
  subset of ``UNIVERSAL_DOGMA_IDS`` (the 10 ``ZEN-*`` ones).
- No production language binding should reference ``ZEN-TEST-*`` or
  ``ZEN-MACRO-*`` IDs.
- All dogma IDs used anywhere must be in ``ALL_DOGMA_IDS``.
- Framework test mappings (in ``languages/*/testing/*/mapping.py``):
  must reference at least one ``ZEN-TEST-*`` or ``ZEN-MACRO-*`` ID.
"""

from __future__ import annotations

import argparse
import importlib
import sys

from pathlib import Path


def main(_check: bool = False) -> int:  # noqa: C901, PLR0912, PLR0915, FBT001, FBT002
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root / "src"))

    from mcp_zen_of_languages.core.universal_dogmas import ALL_DOGMA_IDS
    from mcp_zen_of_languages.core.universal_dogmas import TESTING_STRATEGY_IDS
    from mcp_zen_of_languages.core.universal_dogmas import TESTING_TACTICS_IDS
    from mcp_zen_of_languages.core.universal_dogmas import UNIVERSAL_DOGMA_IDS

    universal_set = set(UNIVERSAL_DOGMA_IDS)
    testing_ids = set(TESTING_TACTICS_IDS) | set(TESTING_STRATEGY_IDS)
    all_ids = set(ALL_DOGMA_IDS)

    errors: list[str] = []
    languages_root = repo_root / "src" / "mcp_zen_of_languages" / "languages"

    # --- 1. Validate top-level production mapping.py files ---
    for lang_dir in sorted(languages_root.iterdir()):
        if not lang_dir.is_dir() or lang_dir.name.startswith("__"):
            continue
        mapping_path = lang_dir / "mapping.py"
        if not mapping_path.exists():
            continue
        module_name = f"mcp_zen_of_languages.languages.{lang_dir.name}.mapping"
        try:
            mod = importlib.import_module(module_name)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{lang_dir.name}/mapping.py: import error: {exc}")
            continue

        full_dogma_ids: list[str] | None = getattr(mod, "FULL_DOGMA_IDS", None)
        if full_dogma_ids is None:
            # Not all mappings export FULL_DOGMA_IDS; skip silently
            continue

        full_dogma_set = set(full_dogma_ids)

        # Must be subset of universal IDs
        non_universal = full_dogma_set - universal_set
        if non_universal:
            errors.append(
                f"{lang_dir.name}/mapping.py: FULL_DOGMA_IDS contains non-universal IDs: "
                f"{sorted(non_universal)}"
            )

        # Must not contain testing-tier IDs
        testing_leak = full_dogma_set & testing_ids
        if testing_leak:
            errors.append(
                f"{lang_dir.name}/mapping.py: FULL_DOGMA_IDS must not reference "
                f"ZEN-TEST-* or ZEN-MACRO-* IDs: {sorted(testing_leak)}"
            )

        # All IDs must be in ALL_DOGMA_IDS
        unknown = full_dogma_set - all_ids
        if unknown:
            errors.append(
                f"{lang_dir.name}/mapping.py: FULL_DOGMA_IDS contains unknown dogma IDs: "
                f"{sorted(unknown)}"
            )

        # Also check detector bindings for testing leaks
        detector_map = getattr(mod, "DETECTOR_MAP", None)
        if detector_map is not None:
            binding_ids = {b.detector_id for b in getattr(detector_map, "bindings", [])}
            errors.extend(
                f"{lang_dir.name}/mapping.py: detector {binding.detector_id!r} "
                f"references testing dogma ID {dogma_id!r} in production mapping"
                for binding in getattr(detector_map, "bindings", [])
                for dogma_id in getattr(binding, "universal_dogma_ids", [])
                if dogma_id in testing_ids
            )
            # Verify universal stub detectors are wired
            _universal_ids = {
                "universal_clutter",
                "universal_control_flow",
                "universal_state_mutation",
                "universal_signature",
                "universal_shared_keyword",
            }
            missing_universal = _universal_ids - binding_ids
            if missing_universal:
                errors.append(
                    f"{lang_dir.name}/mapping.py: missing universal detector(s) "
                    f"{sorted(missing_universal)} — did you extend UNIVERSAL_DETECTOR_MAP?"
                )

    # --- 2. Validate framework mapping.py files ---
    for lang_dir in sorted(languages_root.iterdir()):
        if not lang_dir.is_dir() or lang_dir.name.startswith("__"):
            continue
        testing_dir = lang_dir / "testing"
        if not testing_dir.is_dir():
            continue
        for fw_dir in sorted(testing_dir.iterdir()):
            if not fw_dir.is_dir() or fw_dir.name.startswith("__"):
                continue
            fw_mapping = fw_dir / "mapping.py"
            if not fw_mapping.exists():
                continue
            module_name = (
                f"mcp_zen_of_languages.languages.{lang_dir.name}"
                f".testing.{fw_dir.name}.mapping"
            )
            try:
                fw_mod = importlib.import_module(module_name)
            except Exception as exc:  # noqa: BLE001
                errors.append(
                    f"{lang_dir.name}/testing/{fw_dir.name}/mapping.py: "
                    f"import error: {exc}"
                )
                continue

            full_dogma_ids = getattr(fw_mod, "FULL_DOGMA_IDS", None)
            if full_dogma_ids is None:
                errors.append(
                    f"{lang_dir.name}/testing/{fw_dir.name}/mapping.py: "
                    "missing FULL_DOGMA_IDS"
                )
                continue

            fw_dogma_set = set(full_dogma_ids)

            # Must contain at least one ZEN-TEST-* or ZEN-MACRO-* ID
            has_testing_id = bool(fw_dogma_set & testing_ids)
            if not has_testing_id:
                errors.append(
                    f"{lang_dir.name}/testing/{fw_dir.name}/mapping.py: "
                    "FULL_DOGMA_IDS must reference at least one ZEN-TEST-* or ZEN-MACRO-* ID"
                )

            # All IDs must be in ALL_DOGMA_IDS
            unknown = fw_dogma_set - all_ids
            if unknown:
                errors.append(
                    f"{lang_dir.name}/testing/{fw_dir.name}/mapping.py: "
                    f"FULL_DOGMA_IDS contains unknown dogma IDs: {sorted(unknown)}"
                )

            # Check individual framework detector bindings
            detector_map = getattr(fw_mod, "DETECTOR_MAP", None)
            if detector_map is not None:
                for binding in getattr(detector_map, "bindings", []):
                    dogma_ids = getattr(binding, "universal_dogma_ids", [])
                    if not dogma_ids and binding.rule_ids:
                        errors.append(
                            f"{lang_dir.name}/testing/{fw_dir.name}/mapping.py: "
                            f"detector {binding.detector_id!r} missing explicit testing dogma IDs"
                        )
                    production_leak = set(dogma_ids) & universal_set
                    if production_leak:
                        errors.append(
                            f"{lang_dir.name}/testing/{fw_dir.name}/mapping.py: "
                            f"detector {binding.detector_id!r} uses production dogma IDs: "
                            f"{sorted(production_leak)}"
                        )

    if errors:
        print("Dogma consistency validation failures:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        f"✅ Dogma consistency checks passed ({len(list(languages_root.iterdir()))} languages)"
    )
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate dogma ID tier consistency across language mappings.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Same as normal run; used by pre-commit.",
    )
    args = parser.parse_args()
    raise SystemExit(main(_check=args.check))
