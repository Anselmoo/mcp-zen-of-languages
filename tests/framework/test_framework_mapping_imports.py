"""Import-coverage smoke tests for all framework mapping.py and rules.py modules.

These tests ensure every mapping module and rules module is importable
and contains the expected symbols, driving coverage from 0% to 100%
for those files with no other test coverage.
"""

from __future__ import annotations

from mcp_zen_of_languages.languages.go.testing.gotest.mapping import (
    DETECTOR_MAP as GOTEST_DETECTOR_MAP,
)
from mcp_zen_of_languages.languages.go.testing.gotest.mapping import (
    FULL_DOGMA_IDS as GOTEST_FULL_DOGMA_IDS,
)
from mcp_zen_of_languages.languages.go.testing.gotest.rules import GOTEST_ZEN

# ---------------------------------------------------------------------------
# mapping.py imports — DETECTOR_MAP and FULL_DOGMA_IDS from each framework
# ---------------------------------------------------------------------------
from mcp_zen_of_languages.languages.python.testing.pytest.mapping import (
    DETECTOR_MAP as PYTEST_DETECTOR_MAP,
)
from mcp_zen_of_languages.languages.python.testing.pytest.mapping import (
    FULL_DOGMA_IDS as PYTEST_FULL_DOGMA_IDS,
)

# ---------------------------------------------------------------------------
# rules.py imports — one import per framework
# ---------------------------------------------------------------------------
from mcp_zen_of_languages.languages.python.testing.pytest.rules import PYTEST_ZEN
from mcp_zen_of_languages.languages.ruby.testing.rspec.mapping import (
    DETECTOR_MAP as RSPEC_DETECTOR_MAP,
)
from mcp_zen_of_languages.languages.ruby.testing.rspec.mapping import (
    FULL_DOGMA_IDS as RSPEC_FULL_DOGMA_IDS,
)
from mcp_zen_of_languages.languages.ruby.testing.rspec.rules import RSPEC_ZEN
from mcp_zen_of_languages.languages.typescript.testing.jest.mapping import (
    DETECTOR_MAP as JEST_DETECTOR_MAP,
)
from mcp_zen_of_languages.languages.typescript.testing.jest.mapping import (
    FULL_DOGMA_IDS as JEST_FULL_DOGMA_IDS,
)
from mcp_zen_of_languages.languages.typescript.testing.jest.rules import JEST_ZEN


# ---------------------------------------------------------------------------
# rules.py — principle count assertions
# ---------------------------------------------------------------------------


class TestPytestRules:
    def test_pytest_zen_has_ten_principles(self) -> None:
        assert len(PYTEST_ZEN.principles) == 10

    def test_pytest_zen_language_key(self) -> None:
        assert PYTEST_ZEN.language == "pytest"

    def test_pytest_zen_source_url_set(self) -> None:
        assert PYTEST_ZEN.source_url is not None

    def test_pytest_zen_principle_ids_are_unique(self) -> None:
        ids = [p.id for p in PYTEST_ZEN.principles]
        assert len(ids) == len(set(ids))


class TestJestRules:
    def test_jest_zen_has_ten_principles(self) -> None:
        assert len(JEST_ZEN.principles) == 10

    def test_jest_zen_language_key(self) -> None:
        assert JEST_ZEN.language == "jest"

    def test_jest_zen_source_url_set(self) -> None:
        assert JEST_ZEN.source_url is not None

    def test_jest_zen_principle_ids_are_unique(self) -> None:
        ids = [p.id for p in JEST_ZEN.principles]
        assert len(ids) == len(set(ids))


class TestGotestRules:
    def test_gotest_zen_has_ten_principles(self) -> None:
        assert len(GOTEST_ZEN.principles) == 10

    def test_gotest_zen_language_key(self) -> None:
        assert GOTEST_ZEN.language == "gotest"

    def test_gotest_zen_source_url_set(self) -> None:
        assert GOTEST_ZEN.source_url is not None

    def test_gotest_zen_principle_ids_are_unique(self) -> None:
        ids = [p.id for p in GOTEST_ZEN.principles]
        assert len(ids) == len(set(ids))


class TestRspecRules:
    def test_rspec_zen_has_ten_principles(self) -> None:
        assert len(RSPEC_ZEN.principles) == 10

    def test_rspec_zen_language_key(self) -> None:
        assert RSPEC_ZEN.language == "rspec"

    def test_rspec_zen_source_url_set(self) -> None:
        assert RSPEC_ZEN.source_url is not None

    def test_rspec_zen_principle_ids_are_unique(self) -> None:
        ids = [p.id for p in RSPEC_ZEN.principles]
        assert len(ids) == len(set(ids))


# ---------------------------------------------------------------------------
# mapping.py — DETECTOR_MAP structure assertions
# ---------------------------------------------------------------------------


class TestPytestMapping:
    def test_detector_map_language(self) -> None:
        assert PYTEST_DETECTOR_MAP.language == "pytest"

    def test_detector_map_has_bindings(self) -> None:
        assert len(PYTEST_DETECTOR_MAP.bindings) > 0

    def test_full_dogma_ids_is_non_empty_list(self) -> None:
        assert isinstance(PYTEST_FULL_DOGMA_IDS, list)
        assert len(PYTEST_FULL_DOGMA_IDS) > 0

    def test_all_bindings_have_detector_ids(self) -> None:
        for binding in PYTEST_DETECTOR_MAP.bindings:
            assert binding.detector_id


class TestJestMapping:
    def test_detector_map_language(self) -> None:
        assert JEST_DETECTOR_MAP.language == "jest"

    def test_detector_map_has_bindings(self) -> None:
        assert len(JEST_DETECTOR_MAP.bindings) > 0

    def test_full_dogma_ids_is_non_empty_list(self) -> None:
        assert isinstance(JEST_FULL_DOGMA_IDS, list)
        assert len(JEST_FULL_DOGMA_IDS) > 0

    def test_all_bindings_have_detector_ids(self) -> None:
        for binding in JEST_DETECTOR_MAP.bindings:
            assert binding.detector_id


class TestGotestMapping:
    def test_detector_map_language(self) -> None:
        assert GOTEST_DETECTOR_MAP.language == "gotest"

    def test_detector_map_has_bindings(self) -> None:
        assert len(GOTEST_DETECTOR_MAP.bindings) > 0

    def test_full_dogma_ids_is_non_empty_list(self) -> None:
        assert isinstance(GOTEST_FULL_DOGMA_IDS, list)
        assert len(GOTEST_FULL_DOGMA_IDS) > 0

    def test_all_bindings_have_detector_ids(self) -> None:
        for binding in GOTEST_DETECTOR_MAP.bindings:
            assert binding.detector_id


class TestRspecMapping:
    def test_detector_map_language(self) -> None:
        assert RSPEC_DETECTOR_MAP.language == "rspec"

    def test_detector_map_has_bindings(self) -> None:
        assert len(RSPEC_DETECTOR_MAP.bindings) > 0

    def test_full_dogma_ids_is_non_empty_list(self) -> None:
        assert isinstance(RSPEC_FULL_DOGMA_IDS, list)
        assert len(RSPEC_FULL_DOGMA_IDS) > 0

    def test_all_bindings_have_detector_ids(self) -> None:
        for binding in RSPEC_DETECTOR_MAP.bindings:
            assert binding.detector_id
