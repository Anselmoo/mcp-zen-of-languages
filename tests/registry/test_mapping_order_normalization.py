from __future__ import annotations

from mcp_zen_of_languages.frameworks.angular.mapping import DETECTOR_MAP as ANGULAR_MAP
from mcp_zen_of_languages.frameworks.nextjs.mapping import DETECTOR_MAP as NEXTJS_MAP
from mcp_zen_of_languages.frameworks.pydantic.mapping import (
    DETECTOR_MAP as PYDANTIC_MAP,
)
from mcp_zen_of_languages.frameworks.sqlalchemy.mapping import (
    DETECTOR_MAP as SQLALCHEMY_MAP,
)
from mcp_zen_of_languages.frameworks.vue.mapping import DETECTOR_MAP as VUE_MAP
from mcp_zen_of_languages.languages.bash.mapping import DETECTOR_MAP as BASH_MAP
from mcp_zen_of_languages.languages.cpp.mapping import DETECTOR_MAP as CPP_MAP
from mcp_zen_of_languages.languages.csharp.mapping import DETECTOR_MAP as CSHARP_MAP
from mcp_zen_of_languages.languages.go.mapping import DETECTOR_MAP as GO_MAP
from mcp_zen_of_languages.languages.javascript.mapping import (
    DETECTOR_MAP as JAVASCRIPT_MAP,
)
from mcp_zen_of_languages.languages.powershell.mapping import (
    DETECTOR_MAP as POWERSHELL_MAP,
)
from mcp_zen_of_languages.languages.rust.mapping import DETECTOR_MAP as RUST_MAP
from mcp_zen_of_languages.languages.typescript.mapping import (
    DETECTOR_MAP as TYPESCRIPT_MAP,
)


def _detector_sort_key(detector_id: str) -> tuple[str, int]:
    prefix, _, suffix = detector_id.rpartition("-")
    if suffix.isdigit():
        return prefix, int(suffix)
    return detector_id, -1


def _assert_authored_bindings_are_sorted(detector_map) -> None:
    detector_ids = [binding.detector_id for binding in detector_map.bindings]

    assert detector_ids == sorted(detector_ids, key=_detector_sort_key)
    assert [binding.default_order for binding in detector_map.bindings] == [
        index * 10 for index in range(1, len(detector_map.bindings) + 1)
    ]


def test_rollout_framework_mappings_keep_sorted_authored_binding_order() -> None:
    for detector_map in (
        ANGULAR_MAP,
        NEXTJS_MAP,
        PYDANTIC_MAP,
        SQLALCHEMY_MAP,
        VUE_MAP,
    ):
        _assert_authored_bindings_are_sorted(detector_map)


def test_rollout_language_mappings_keep_sorted_authored_binding_order() -> None:
    for detector_map in (
        BASH_MAP,
        CPP_MAP,
        CSHARP_MAP,
        GO_MAP,
        JAVASCRIPT_MAP,
        POWERSHELL_MAP,
        RUST_MAP,
        TYPESCRIPT_MAP,
    ):
        _assert_authored_bindings_are_sorted(detector_map)
