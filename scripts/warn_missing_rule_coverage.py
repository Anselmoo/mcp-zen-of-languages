from __future__ import annotations

from mcp_zen_of_languages.rules import get_all_languages, get_language_zen
from mcp_zen_of_languages.rules.base_models import get_missing_detector_rules


def main() -> int:
    gaps: dict[str, list[str]] = {}
    for language in get_all_languages():
        lang_zen = get_language_zen(language)
        if not lang_zen:
            continue
        if missing := get_missing_detector_rules(lang_zen, explicit_only=True):
            gaps[language] = missing

    if not gaps:
        print("All rules have explicit detector coverage.")
        return 0

    print("WARNING: Missing explicit detector coverage for some rules.")
    for language, missing in sorted(gaps.items()):
        missing_list = ", ".join(missing)
        print(f" - {language}: {missing_list}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
