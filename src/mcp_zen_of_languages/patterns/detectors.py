"""Concrete architectural pattern detectors.

Each ``PatternDetector`` subclass scans raw source text for one well-known
structural pattern.  Detectors use compiled regular expressions so they are
language-agnostic — the ``language`` argument is accepted for future
specialisation but is not used as a gate today.

All detectors are collected in the module-level ``ALL_DETECTORS`` list, which
is the single integration point consumed by ``detect_patterns`` and the
``check_architectural_patterns`` MCP tool.
"""

# ruff: noqa: ARG002
from __future__ import annotations

import re

from abc import ABC
from abc import abstractmethod

from mcp_zen_of_languages.models import Location
from mcp_zen_of_languages.models import PatternFinding


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _find_location(code: str, pattern: re.Pattern[str]) -> Location | None:
    """Return the 1-based location of the first regex match in *code*.

    Args:
        code: Multi-line source text to scan.
        pattern: Compiled regular expression to search for.

    Returns:
        A ``Location`` pointing at the matched line and column, or ``None``
        when the pattern is not found.
    """
    for i, line in enumerate(code.splitlines(), 1):
        m = pattern.search(line)
        if m:
            return Location(line=i, column=m.start() + 1)
    return None


def _has_pattern(code: str, pattern: re.Pattern[str]) -> bool:
    """Return ``True`` when *pattern* matches anywhere in *code*."""
    return bool(pattern.search(code))


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------


class PatternDetector(ABC):
    """Abstract base for all architectural pattern detectors.

    Subclasses implement ``detect`` to inspect a source snippet and return
    zero or more ``PatternFinding`` objects.  Returning an empty list simply
    means the pattern was not recognised — it is not an error condition.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Canonical pattern name emitted in every finding (e.g. ``"singleton"``)."""

    @abstractmethod
    def detect(self, code: str, language: str) -> list[PatternFinding]:
        """Scan *code* for the pattern and return all findings.

        Args:
            code: Source fragment to inspect.
            language: Canonical language key — accepted for future use.

        Returns:
            List of ``PatternFinding`` objects, possibly empty.
        """


# ---------------------------------------------------------------------------
# Concrete detectors
# ---------------------------------------------------------------------------


class SingletonDetector(PatternDetector):
    """Detect the Singleton design pattern.

    Looks for a class that combines a private ``_instance``/``__instance``
    field with a ``get_instance``/``getInstance`` accessor — the canonical
    lazy-init singleton structure across Python, Java, TypeScript, and Go.
    """

    _INSTANCE_RE = re.compile(r"\b_?_?instance\b", re.IGNORECASE)
    _ACCESSOR_RE = re.compile(r"\bget_?[Ii]nstance\b")

    @property
    def name(self) -> str:
        """Return the canonical pattern identifier ``"singleton"``."""
        return "singleton"

    def detect(self, code: str, language: str) -> list[PatternFinding]:
        """Return a finding when singleton indicators are present."""
        if not (
            _has_pattern(code, self._INSTANCE_RE)
            and _has_pattern(code, self._ACCESSOR_RE)
        ):
            return []
        location = _find_location(code, self._ACCESSOR_RE) or _find_location(
            code, self._INSTANCE_RE
        )
        return [
            PatternFinding(
                name=self.name,
                location=location,
                details="Private instance field combined with a get_instance accessor.",
            )
        ]


class FactoryDetector(PatternDetector):
    """Detect Factory Method / Abstract Factory patterns.

    Matches classes whose name ends in ``Factory`` or methods that begin with
    ``create_``, ``make_``, or ``build_`` followed by a word character — the
    conventional factory-function naming style across most languages.
    """

    _CLASS_RE = re.compile(r"\bclass\s+\w*Factory\b")
    _METHOD_RE = re.compile(
        r"\b(?:def|function|func)\s+(?:create|make|build)_?\w+\s*[(\[]"
    )

    @property
    def name(self) -> str:
        """Return the canonical pattern identifier ``"factory"``."""
        return "factory"

    def detect(self, code: str, language: str) -> list[PatternFinding]:
        """Return a finding when a Factory class or factory method is found."""
        class_match = _has_pattern(code, self._CLASS_RE)
        method_match = _has_pattern(code, self._METHOD_RE)
        if not (class_match or method_match):
            return []
        primary = self._CLASS_RE if class_match else self._METHOD_RE
        location = _find_location(code, primary)
        detail = (
            "Class named *Factory detected."
            if class_match
            else "Factory method (create_*/make_*/build_*) detected."
        )
        return [PatternFinding(name=self.name, location=location, details=detail)]


class ObserverDetector(PatternDetector):
    """Detect the Observer / Event Emitter pattern.

    Recognises the subscribe/unsubscribe pair, the addEventListener/
    removeEventListener pair, or a notify/emit combination — all canonical
    Observer-pattern method names across Python, JavaScript, and Java.
    """

    _SUBSCRIBE_RE = re.compile(r"\bsubscribe\b")
    _UNSUBSCRIBE_RE = re.compile(r"\bunsubscribe\b")
    _ADD_LISTENER_RE = re.compile(r"\baddEventListener\b")
    _REMOVE_LISTENER_RE = re.compile(r"\bremoveEventListener\b")
    _NOTIFY_RE = re.compile(r"\bnotify\b")
    _EMIT_RE = re.compile(r"\bemit\b")

    @property
    def name(self) -> str:
        """Return the canonical pattern identifier ``"observer"``."""
        return "observer"

    def detect(self, code: str, language: str) -> list[PatternFinding]:
        """Return a finding when observer-pattern method names are present."""
        sub_pair = _has_pattern(code, self._SUBSCRIBE_RE) and _has_pattern(
            code, self._UNSUBSCRIBE_RE
        )
        listener_pair = _has_pattern(code, self._ADD_LISTENER_RE) and _has_pattern(
            code, self._REMOVE_LISTENER_RE
        )
        notify_emit = _has_pattern(code, self._NOTIFY_RE) and _has_pattern(
            code, self._EMIT_RE
        )

        if not (sub_pair or listener_pair or notify_emit):
            return []

        if sub_pair:
            location = _find_location(code, self._SUBSCRIBE_RE)
            detail = "subscribe/unsubscribe pair detected."
        elif listener_pair:
            location = _find_location(code, self._ADD_LISTENER_RE)
            detail = "addEventListener/removeEventListener pair detected."
        else:
            location = _find_location(code, self._NOTIFY_RE)
            detail = "notify/emit pair detected."

        return [PatternFinding(name=self.name, location=location, details=detail)]


class RepositoryDetector(PatternDetector):
    """Detect the Repository pattern.

    A repository class exposes a ``find_by_*`` / ``findBy*`` query method
    alongside a persistence method (``save``, ``delete``, ``remove``, or
    ``persist``).  This combination is the standard Repository pattern
    signature in DDD-influenced codebases.
    """

    _FIND_RE = re.compile(r"\bfind_?[Bb]y\w*\b")
    _PERSIST_RE = re.compile(r"\b(?:save|delete|remove|persist)\b")

    @property
    def name(self) -> str:
        """Return the canonical pattern identifier ``"repository"``."""
        return "repository"

    def detect(self, code: str, language: str) -> list[PatternFinding]:
        """Return a finding when both query and persistence methods are present."""
        if not (
            _has_pattern(code, self._FIND_RE) and _has_pattern(code, self._PERSIST_RE)
        ):
            return []
        location = _find_location(code, self._FIND_RE)
        return [
            PatternFinding(
                name=self.name,
                location=location,
                details="find_by_* query method combined with a save/delete persistence method.",
            )
        ]


class BuilderDetector(PatternDetector):
    """Detect the Builder pattern.

    A builder class exposes a ``build()`` terminator plus two or more
    ``with_*`` / ``set_*`` (Python) or ``with*`` / ``set*`` (camelCase)
    configuration methods — the fluent-interface Builder signature.
    """

    _BUILD_RE = re.compile(r"\bbuild\s*\(")
    _WITH_RE = re.compile(r"\b(?:with|set)_?\w+\s*\(")

    @property
    def name(self) -> str:
        """Return the canonical pattern identifier ``"builder"``."""
        return "builder"

    def detect(self, code: str, language: str) -> list[PatternFinding]:
        """Return a finding when a build() terminator and fluent setters are present."""
        if not _has_pattern(code, self._BUILD_RE):
            return []
        with_matches = self._WITH_RE.findall(code)
        if len(with_matches) < 2:  # noqa: PLR2004
            return []
        location = _find_location(code, self._BUILD_RE)
        return [
            PatternFinding(
                name=self.name,
                location=location,
                details=f"build() terminator with {len(with_matches)} fluent setter(s) detected.",
            )
        ]


class CommandDetector(PatternDetector):
    """Detect the Command design pattern.

    Matches classes that expose an ``execute()`` method.  When an ``undo()``
    or ``redo()`` method is also present the detail string notes the richer
    reversible-command structure.
    """

    _EXECUTE_RE = re.compile(r"\bexecute\s*\(")
    _UNDO_RE = re.compile(r"\bundo\s*\(")
    _REDO_RE = re.compile(r"\bredo\s*\(")

    @property
    def name(self) -> str:
        """Return the canonical pattern identifier ``"command"``."""
        return "command"

    def detect(self, code: str, language: str) -> list[PatternFinding]:
        """Return a finding when an execute() method is present."""
        if not _has_pattern(code, self._EXECUTE_RE):
            return []
        location = _find_location(code, self._EXECUTE_RE)
        has_undo = _has_pattern(code, self._UNDO_RE)
        has_redo = _has_pattern(code, self._REDO_RE)
        if has_undo or has_redo:
            extras = " and ".join(
                filter(
                    None, ["undo()" if has_undo else "", "redo()" if has_redo else ""]
                )
            )
            detail = f"execute() with reversible {extras} detected."
        else:
            detail = "execute() method detected."
        return [PatternFinding(name=self.name, location=location, details=detail)]


class MVCDetector(PatternDetector):
    """Detect the MVC (Model-View-Controller) architectural pattern.

    Looks for identifiers ending in ``Model``, ``View``, and ``Controller``
    (case-sensitive suffix).  At least two of the three layers must be present
    to emit a finding, since a lone ``*Model`` class does not imply MVC.
    """

    _MODEL_RE = re.compile(r"\b\w+Model\b")
    _VIEW_RE = re.compile(r"\b\w+View\b")
    _CONTROLLER_RE = re.compile(r"\b\w+Controller\b")

    @property
    def name(self) -> str:
        """Return the canonical pattern identifier ``"mvc"``."""
        return "mvc"

    def detect(self, code: str, language: str) -> list[PatternFinding]:
        """Return a finding when at least two MVC layers are identified."""
        layers: list[tuple[str, re.Pattern[str]]] = [
            ("Model", self._MODEL_RE),
            ("View", self._VIEW_RE),
            ("Controller", self._CONTROLLER_RE),
        ]
        found = [
            (label, pattern) for label, pattern in layers if _has_pattern(code, pattern)
        ]
        if len(found) < 2:  # noqa: PLR2004
            return []
        _, primary_pattern = found[0]
        location = _find_location(code, primary_pattern)
        present = ", ".join(label for label, _ in found)
        return [
            PatternFinding(
                name=self.name,
                location=location,
                details=f"MVC layers detected: {present}.",
            )
        ]


class MiddlewareDetector(PatternDetector):
    """Detect middleware / pipeline-stage patterns.

    Recognises two common forms:

    * A class whose name ends in ``Middleware``.
    * A function/method that accepts a ``next`` parameter — the standard
      Express.js, Koa, Django, and Go ``http.Handler`` middleware signature.
    """

    _CLASS_RE = re.compile(r"\bclass\s+\w*[Mm]iddleware\b")
    _NEXT_PARAM_RE = re.compile(r"\((?:[^)]*,\s*)?\bnext\b(?:\s*[:,)]|$)")

    @property
    def name(self) -> str:
        """Return the canonical pattern identifier ``"middleware"``."""
        return "middleware"

    def detect(self, code: str, language: str) -> list[PatternFinding]:
        """Return a finding when a middleware class or next-parameter function is found."""
        class_match = _has_pattern(code, self._CLASS_RE)
        next_match = _has_pattern(code, self._NEXT_PARAM_RE)
        if not (class_match or next_match):
            return []
        primary = self._CLASS_RE if class_match else self._NEXT_PARAM_RE
        location = _find_location(code, primary)
        detail = (
            "Class named *Middleware detected."
            if class_match
            else "Function with a 'next' parameter (middleware chain) detected."
        )
        return [PatternFinding(name=self.name, location=location, details=detail)]


class PrototypeDetector(PatternDetector):
    """Detect the Prototype design pattern.

    Looks for a ``clone()`` / ``Clone()`` method — the canonical way to copy
    an object in Python, Go, and Rust without knowing its concrete type.
    Rust's ``Clone`` trait derive macro is also matched via a ``#[derive``
    attribute that includes ``Clone``.
    """

    _CLONE_RE = re.compile(r"\bclone\s*\(|\bClone\s*\(|\bClone\b")

    @property
    def name(self) -> str:
        """Return the canonical pattern identifier ``"prototype"``."""
        return "prototype"

    def detect(self, code: str, language: str) -> list[PatternFinding]:
        """Return a finding when a clone/Clone method or trait is present."""
        if not _has_pattern(code, self._CLONE_RE):
            return []
        location = _find_location(code, self._CLONE_RE)
        return [
            PatternFinding(
                name=self.name,
                location=location,
                details="clone()/Clone() method or Clone trait detected.",
            )
        ]


class DecoratorPatternDetector(PatternDetector):
    """Detect the Decorator structural pattern.

    Recognises classes named ``*Decorator`` or classes that hold a
    ``_wrapped`` / ``_component`` / ``_wrappee`` field — the two common
    ways to implement structural decoration across Python, Go, and Java.
    """

    _CLASS_RE = re.compile(r"\bclass\s+\w*Decorator\b")
    _WRAPPED_RE = re.compile(r"\b(?:_wrapped|_component|_wrappee)\b")

    @property
    def name(self) -> str:
        """Return the canonical pattern identifier ``"decorator"``."""
        return "decorator"

    def detect(self, code: str, language: str) -> list[PatternFinding]:
        """Return a finding when a Decorator class or wrappee field is found."""
        class_match = _has_pattern(code, self._CLASS_RE)
        field_match = _has_pattern(code, self._WRAPPED_RE)
        if not (class_match or field_match):
            return []
        primary = self._CLASS_RE if class_match else self._WRAPPED_RE
        location = _find_location(code, primary)
        detail = (
            "Class named *Decorator detected."
            if class_match
            else "Wrappee/component field (_wrapped/_component/_wrappee) detected."
        )
        return [PatternFinding(name=self.name, location=location, details=detail)]


class FacadeDetector(PatternDetector):
    """Detect the Facade structural pattern.

    Matches classes whose name ends in ``Facade`` — the conventional way to
    signal a simplified entry point to a complex subsystem.
    """

    _CLASS_RE = re.compile(r"\bclass\s+\w*Facade\b")

    @property
    def name(self) -> str:
        """Return the canonical pattern identifier ``"facade"``."""
        return "facade"

    def detect(self, code: str, language: str) -> list[PatternFinding]:
        """Return a finding when a Facade class is present."""
        if not _has_pattern(code, self._CLASS_RE):
            return []
        location = _find_location(code, self._CLASS_RE)
        return [
            PatternFinding(
                name=self.name,
                location=location,
                details="Class named *Facade detected.",
            )
        ]


class ProxyDetector(PatternDetector):
    """Detect the Proxy structural pattern.

    Matches classes whose name ends in ``Proxy`` — a standard naming
    convention across Python, Go, Java, and TypeScript to mark classes that
    control access to a real subject.
    """

    _CLASS_RE = re.compile(r"\bclass\s+\w*Proxy\b")

    @property
    def name(self) -> str:
        """Return the canonical pattern identifier ``"proxy"``."""
        return "proxy"

    def detect(self, code: str, language: str) -> list[PatternFinding]:
        """Return a finding when a Proxy class is present."""
        if not _has_pattern(code, self._CLASS_RE):
            return []
        location = _find_location(code, self._CLASS_RE)
        return [
            PatternFinding(
                name=self.name,
                location=location,
                details="Class named *Proxy detected.",
            )
        ]


class StrategyDetector(PatternDetector):
    """Detect the Strategy behavioural pattern.

    Looks for a ``set_strategy()`` / ``setStrategy()`` setter or a
    ``_strategy`` field — both indicate a context class that holds an
    interchangeable algorithm object.
    """

    _SETTER_RE = re.compile(r"\bset_?[Ss]trategy\s*\(")
    _FIELD_RE = re.compile(r"\b_strategy\b")

    @property
    def name(self) -> str:
        """Return the canonical pattern identifier ``"strategy"``."""
        return "strategy"

    def detect(self, code: str, language: str) -> list[PatternFinding]:
        """Return a finding when a strategy setter or field is present."""
        setter_match = _has_pattern(code, self._SETTER_RE)
        field_match = _has_pattern(code, self._FIELD_RE)
        if not (setter_match or field_match):
            return []
        primary = self._SETTER_RE if setter_match else self._FIELD_RE
        location = _find_location(code, primary)
        detail = (
            "set_strategy() setter detected."
            if setter_match
            else "_strategy field indicating interchangeable algorithm detected."
        )
        return [PatternFinding(name=self.name, location=location, details=detail)]


class CompositeDetector(PatternDetector):
    """Detect the Composite structural pattern.

    Recognises ``add_child()`` / ``addChild()`` paired with either
    ``remove_child()`` / ``removeChild()`` or a ``children`` collection —
    the hallmark of a tree-structure Composite component.
    """

    _ADD_RE = re.compile(r"\badd_?[Cc]hild\s*\(")
    _REMOVE_RE = re.compile(r"\bremove_?[Cc]hild\s*\(")
    _CHILDREN_RE = re.compile(r"\bchildren\b")

    @property
    def name(self) -> str:
        """Return the canonical pattern identifier ``"composite"``."""
        return "composite"

    def detect(self, code: str, language: str) -> list[PatternFinding]:
        """Return a finding when an add_child method and child collection are present."""
        if not _has_pattern(code, self._ADD_RE):
            return []
        has_remove = _has_pattern(code, self._REMOVE_RE)
        has_children = _has_pattern(code, self._CHILDREN_RE)
        if not (has_remove or has_children):
            return []
        location = _find_location(code, self._ADD_RE)
        detail = (
            "add_child()/remove_child() pair detected."
            if has_remove
            else "add_child() with a children collection detected."
        )
        return [PatternFinding(name=self.name, location=location, details=detail)]


class ChainOfResponsibilityDetector(PatternDetector):
    """Detect the Chain of Responsibility behavioural pattern.

    Matches a ``set_next()`` / ``setNext()`` linker combined with a
    ``handle()`` dispatcher — the standard Chain of Responsibility API
    across Python, Go, Java, and TypeScript.
    """

    _NEXT_RE = re.compile(r"\bset_?[Nn]ext\s*\(")
    _HANDLE_RE = re.compile(r"\bhandle\s*\(")

    @property
    def name(self) -> str:
        """Return the canonical pattern identifier ``"chain_of_responsibility"``."""
        return "chain_of_responsibility"

    def detect(self, code: str, language: str) -> list[PatternFinding]:
        """Return a finding when set_next() and handle() are both present."""
        if not (
            _has_pattern(code, self._NEXT_RE) and _has_pattern(code, self._HANDLE_RE)
        ):
            return []
        location = _find_location(code, self._NEXT_RE)
        return [
            PatternFinding(
                name=self.name,
                location=location,
                details="set_next()/setNext() linker combined with handle() dispatcher detected.",
            )
        ]


class IteratorDetector(PatternDetector):
    """Detect the Iterator behavioural pattern.

    Recognises two canonical forms:

    * Python dunder protocol: ``__iter__`` + ``__next__`` present in the
      same snippet.
    * Cross-language API: ``has_next()`` / ``hasNext()`` + ``next()`` —
      the standard iterator interface in Java, Go, and many other languages.
    """

    _ITER_RE = re.compile(r"\b__iter__\b")
    _NEXT_DUNDER_RE = re.compile(r"\b__next__\b")
    _HAS_NEXT_RE = re.compile(r"\b[Hh]as_?[Nn]ext\s*\(")
    _NEXT_METHOD_RE = re.compile(r"\b[Nn]ext\s*\(")

    @property
    def name(self) -> str:
        """Return the canonical pattern identifier ``"iterator"``."""
        return "iterator"

    def detect(self, code: str, language: str) -> list[PatternFinding]:
        """Return a finding when iterator protocol methods are present."""
        dunder_iter = _has_pattern(code, self._ITER_RE) and _has_pattern(
            code, self._NEXT_DUNDER_RE
        )
        method_iter = _has_pattern(code, self._HAS_NEXT_RE) and _has_pattern(
            code, self._NEXT_METHOD_RE
        )
        if not (dunder_iter or method_iter):
            return []
        if dunder_iter:
            location = _find_location(code, self._ITER_RE)
            detail = "__iter__/__next__ protocol detected."
        else:
            location = _find_location(code, self._HAS_NEXT_RE)
            detail = "has_next()/next() iterator API detected."
        return [PatternFinding(name=self.name, location=location, details=detail)]


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

ALL_DETECTORS: list[PatternDetector] = [
    SingletonDetector(),
    FactoryDetector(),
    ObserverDetector(),
    RepositoryDetector(),
    BuilderDetector(),
    CommandDetector(),
    MVCDetector(),
    MiddlewareDetector(),
    PrototypeDetector(),
    DecoratorPatternDetector(),
    FacadeDetector(),
    ProxyDetector(),
    StrategyDetector(),
    CompositeDetector(),
    ChainOfResponsibilityDetector(),
    IteratorDetector(),
]
"""All registered pattern detectors, applied in order by ``detect_patterns``."""
