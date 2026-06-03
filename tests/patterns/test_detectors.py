from __future__ import annotations

import pytest

from mcp_zen_of_languages.patterns.detectors import ALL_DETECTORS
from mcp_zen_of_languages.patterns.detectors import BuilderDetector
from mcp_zen_of_languages.patterns.detectors import ChainOfResponsibilityDetector
from mcp_zen_of_languages.patterns.detectors import CommandDetector
from mcp_zen_of_languages.patterns.detectors import CompositeDetector
from mcp_zen_of_languages.patterns.detectors import DecoratorPatternDetector
from mcp_zen_of_languages.patterns.detectors import FacadeDetector
from mcp_zen_of_languages.patterns.detectors import FactoryDetector
from mcp_zen_of_languages.patterns.detectors import IteratorDetector
from mcp_zen_of_languages.patterns.detectors import MVCDetector
from mcp_zen_of_languages.patterns.detectors import MiddlewareDetector
from mcp_zen_of_languages.patterns.detectors import ObserverDetector
from mcp_zen_of_languages.patterns.detectors import PrototypeDetector
from mcp_zen_of_languages.patterns.detectors import ProxyDetector
from mcp_zen_of_languages.patterns.detectors import RepositoryDetector
from mcp_zen_of_languages.patterns.detectors import SingletonDetector
from mcp_zen_of_languages.patterns.detectors import StrategyDetector


# ---------------------------------------------------------------------------
# SingletonDetector
# ---------------------------------------------------------------------------

SINGLETON_CODE = """\
class Config:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
"""

SINGLETON_JS = """\
class Config {
    static _instance = null;
    static getInstance() {
        if (!Config._instance) Config._instance = new Config();
        return Config._instance;
    }
}
"""


def test_singleton_detects_python():
    findings = SingletonDetector().detect(SINGLETON_CODE, "python")
    assert len(findings) == 1
    assert findings[0].name == "singleton"
    assert findings[0].location is not None
    assert findings[0].details is not None


def test_singleton_detects_javascript():
    findings = SingletonDetector().detect(SINGLETON_JS, "javascript")
    assert len(findings) == 1
    assert findings[0].name == "singleton"


def test_singleton_no_match():
    findings = SingletonDetector().detect("def foo(): pass", "python")
    assert findings == []


def test_singleton_instance_without_accessor():
    code = "class Foo:\n    _instance = None\n"
    assert SingletonDetector().detect(code, "python") == []


# ---------------------------------------------------------------------------
# FactoryDetector
# ---------------------------------------------------------------------------

FACTORY_CLASS_CODE = """\
class UserFactory:
    def create(self, **kwargs):
        return User(**kwargs)
"""

FACTORY_METHOD_CODE = """\
def create_user(name: str) -> User:
    return User(name=name)
"""

FACTORY_JS = """\
function createWidget(type) {
    return new Widget(type);
}
"""


def test_factory_detects_class():
    findings = FactoryDetector().detect(FACTORY_CLASS_CODE, "python")
    assert len(findings) == 1
    assert findings[0].name == "factory"
    assert findings[0].location is not None


def test_factory_detects_method():
    findings = FactoryDetector().detect(FACTORY_METHOD_CODE, "python")
    assert len(findings) == 1
    assert findings[0].name == "factory"


def test_factory_detects_js_function():
    findings = FactoryDetector().detect(FACTORY_JS, "javascript")
    assert len(findings) == 1
    assert findings[0].name == "factory"


def test_factory_no_match():
    assert FactoryDetector().detect("x = 1", "python") == []


# ---------------------------------------------------------------------------
# ObserverDetector
# ---------------------------------------------------------------------------

OBSERVER_SUBSCRIBE = """\
class EventBus:
    def subscribe(self, listener): self._listeners.append(listener)
    def unsubscribe(self, listener): self._listeners.remove(listener)
    def notify(self, event): ...
"""

OBSERVER_LISTENER = """\
element.addEventListener('click', handler);
element.removeEventListener('click', handler);
"""

OBSERVER_NOTIFY_EMIT = """\
class Emitter:
    def notify(self): ...
    def emit(self, event): ...
"""


def test_observer_subscribe_pair():
    findings = ObserverDetector().detect(OBSERVER_SUBSCRIBE, "python")
    assert len(findings) == 1
    assert findings[0].name == "observer"
    assert "subscribe" in (findings[0].details or "")


def test_observer_add_listener_pair():
    findings = ObserverDetector().detect(OBSERVER_LISTENER, "javascript")
    assert len(findings) == 1
    assert "addEventListener" in (findings[0].details or "")


def test_observer_notify_emit():
    findings = ObserverDetector().detect(OBSERVER_NOTIFY_EMIT, "python")
    assert len(findings) == 1
    assert "notify" in (findings[0].details or "")


def test_observer_no_match():
    assert ObserverDetector().detect("def foo(): pass", "python") == []


def test_observer_subscribe_without_unsubscribe():
    assert ObserverDetector().detect("def subscribe(): pass", "python") == []


# ---------------------------------------------------------------------------
# RepositoryDetector
# ---------------------------------------------------------------------------

REPO_CODE = """\
class UserRepository:
    def find_by_id(self, id): ...
    def find_by_email(self, email): ...
    def save(self, user): ...
    def delete(self, user): ...
"""

REPO_CAMEL = """\
class OrderRepo {
    findByStatus(status) { ... }
    save(order) { ... }
}
"""


def test_repository_detects_python():
    findings = RepositoryDetector().detect(REPO_CODE, "python")
    assert len(findings) == 1
    assert findings[0].name == "repository"
    assert findings[0].location is not None


def test_repository_detects_camelcase():
    findings = RepositoryDetector().detect(REPO_CAMEL, "javascript")
    assert len(findings) == 1
    assert findings[0].name == "repository"


def test_repository_find_without_persist():
    assert RepositoryDetector().detect("def find_by_id(id): ...", "python") == []


def test_repository_persist_without_find():
    assert RepositoryDetector().detect("def save(x): ...", "python") == []


# ---------------------------------------------------------------------------
# BuilderDetector
# ---------------------------------------------------------------------------

BUILDER_CODE = """\
class QueryBuilder:
    def with_filter(self, f):
        self._filter = f
        return self

    def set_limit(self, n):
        self._limit = n
        return self

    def build(self):
        return Query(self._filter, self._limit)
"""


def test_builder_detects():
    findings = BuilderDetector().detect(BUILDER_CODE, "python")
    assert len(findings) == 1
    assert findings[0].name == "builder"
    assert findings[0].location is not None
    assert "2" in (findings[0].details or "")


def test_builder_only_build():
    assert BuilderDetector().detect("def build(self): return self", "python") == []


def test_builder_one_setter():
    code = "def with_x(self): return self\ndef build(self): return self\n"
    assert BuilderDetector().detect(code, "python") == []


# ---------------------------------------------------------------------------
# CommandDetector
# ---------------------------------------------------------------------------

COMMAND_CODE = """\
class DeleteCommand:
    def execute(self):
        self._db.delete(self._item)

    def undo(self):
        self._db.insert(self._item)
"""

COMMAND_SIMPLE = """\
class PrintCommand:
    def execute(self):
        print(self._text)
"""


def test_command_with_undo():
    findings = CommandDetector().detect(COMMAND_CODE, "python")
    assert len(findings) == 1
    assert findings[0].name == "command"
    assert "undo()" in (findings[0].details or "")


def test_command_simple():
    findings = CommandDetector().detect(COMMAND_SIMPLE, "python")
    assert len(findings) == 1
    assert findings[0].name == "command"
    assert findings[0].details == "execute() method detected."


def test_command_no_execute():
    assert CommandDetector().detect("def run(self): pass", "python") == []


def test_command_redo_only():
    code = "def execute(self): ...\ndef redo(self): ...\n"
    findings = CommandDetector().detect(code, "python")
    assert len(findings) == 1
    assert "redo()" in (findings[0].details or "")


# ---------------------------------------------------------------------------
# MVCDetector
# ---------------------------------------------------------------------------

MVC_CODE = """\
class UserModel:
    pass

class UserView:
    pass

class UserController:
    pass
"""

MVC_TWO_LAYERS = """\
class ProductModel:
    pass

class ProductView:
    pass
"""


def test_mvc_three_layers():
    findings = MVCDetector().detect(MVC_CODE, "python")
    assert len(findings) == 1
    assert findings[0].name == "mvc"
    assert "Model" in (findings[0].details or "")
    assert "View" in (findings[0].details or "")
    assert "Controller" in (findings[0].details or "")


def test_mvc_two_layers():
    findings = MVCDetector().detect(MVC_TWO_LAYERS, "python")
    assert len(findings) == 1
    assert findings[0].name == "mvc"


def test_mvc_one_layer_no_match():
    assert MVCDetector().detect("class UserModel: pass", "python") == []


def test_mvc_no_match():
    assert MVCDetector().detect("x = 1", "python") == []


# ---------------------------------------------------------------------------
# MiddlewareDetector
# ---------------------------------------------------------------------------

MIDDLEWARE_CLASS = """\
class AuthMiddleware:
    def process(self, request, next):
        ...
"""

MIDDLEWARE_NEXT = """\
def logging_middleware(request, response, next):
    log(request)
    next()
"""

MIDDLEWARE_EXPRESS = """\
app.use(function(req, res, next) {
    console.log('request');
    next();
});
"""


def test_middleware_class():
    findings = MiddlewareDetector().detect(MIDDLEWARE_CLASS, "python")
    assert len(findings) == 1
    assert findings[0].name == "middleware"
    assert "Middleware" in (findings[0].details or "")


def test_middleware_next_param():
    findings = MiddlewareDetector().detect(MIDDLEWARE_NEXT, "python")
    assert len(findings) == 1
    assert findings[0].name == "middleware"
    assert "next" in (findings[0].details or "")


def test_middleware_express_style():
    findings = MiddlewareDetector().detect(MIDDLEWARE_EXPRESS, "javascript")
    assert len(findings) == 1
    assert findings[0].name == "middleware"


def test_middleware_no_match():
    assert MiddlewareDetector().detect("def foo(a, b): pass", "python") == []


# ---------------------------------------------------------------------------
# ALL_DETECTORS registry
# ---------------------------------------------------------------------------


def test_all_detectors_count():
    assert len(ALL_DETECTORS) == 16


def test_all_detectors_unique_names():
    names = [d.name for d in ALL_DETECTORS]
    assert len(names) == len(set(names))


def test_all_detectors_empty_code():
    for detector in ALL_DETECTORS:
        assert detector.detect("", "python") == []


# ---------------------------------------------------------------------------
# Public API: detect_patterns()
# ---------------------------------------------------------------------------


def test_detect_patterns_finds_factory():
    from mcp_zen_of_languages.patterns import detect_patterns

    findings = detect_patterns(
        "class UserFactory:\n    def create(self): ...\n", "python"
    )
    assert any(f.name == "factory" for f in findings)


def test_detect_patterns_empty_returns_empty():
    from mcp_zen_of_languages.patterns import detect_patterns

    assert detect_patterns("", "python") == []


# ---------------------------------------------------------------------------
# Internal helper: _find_location
# ---------------------------------------------------------------------------


def test_find_location_no_match():
    import re

    from mcp_zen_of_languages.patterns.detectors import _find_location

    result = _find_location("def foo(): pass", re.compile(r"\bBAR_NEVER_MATCHES\b"))
    assert result is None


def test_find_location_returns_correct_position():
    import re

    from mcp_zen_of_languages.patterns.detectors import _find_location

    result = _find_location("line1\nclass Foo:\n", re.compile(r"\bclass\b"))
    assert result is not None
    assert result.line == 2
    assert result.column == 1


# ---------------------------------------------------------------------------
# Location accuracy
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("code", "detector", "expected_line"),
    [
        (SINGLETON_CODE, SingletonDetector(), 5),  # get_instance on line 5
        (FACTORY_CLASS_CODE, FactoryDetector(), 1),  # class UserFactory on line 1
        (OBSERVER_SUBSCRIBE, ObserverDetector(), 2),  # subscribe on line 2
        (REPO_CODE, RepositoryDetector(), 2),  # find_by_id on line 2
        (BUILDER_CODE, BuilderDetector(), 10),  # build( on line 10
        (COMMAND_CODE, CommandDetector(), 2),  # execute( on line 2
        (MVC_CODE, MVCDetector(), 1),  # UserModel on line 1
        (MIDDLEWARE_CLASS, MiddlewareDetector(), 1),  # AuthMiddleware on line 1
    ],
)
def test_location_line(code, detector, expected_line):
    findings = detector.detect(code, "python")
    assert len(findings) >= 1
    assert findings[0].location is not None
    assert findings[0].location.line == expected_line


# ---------------------------------------------------------------------------
# PrototypeDetector
# ---------------------------------------------------------------------------

PROTOTYPE_PY = """\
class Shape:
    def clone(self):
        return copy.deepcopy(self)
"""

PROTOTYPE_GO = """\
type Shape struct{ ... }
func (s Shape) Clone() Shape { return s }
"""

PROTOTYPE_RUST = "#[derive(Clone, Debug)]\nstruct Config { value: i32 }\n"


def test_prototype_python():
    findings = PrototypeDetector().detect(PROTOTYPE_PY, "python")
    assert len(findings) == 1
    assert findings[0].name == "prototype"


def test_prototype_go():
    findings = PrototypeDetector().detect(PROTOTYPE_GO, "go")
    assert len(findings) == 1
    assert findings[0].name == "prototype"


def test_prototype_rust_derive():
    findings = PrototypeDetector().detect(PROTOTYPE_RUST, "rust")
    assert len(findings) == 1
    assert findings[0].name == "prototype"


def test_prototype_no_match():
    assert PrototypeDetector().detect("def foo(): pass", "python") == []


# ---------------------------------------------------------------------------
# DecoratorPatternDetector
# ---------------------------------------------------------------------------

DECORATOR_CLASS_CODE = """\
class LoggingDecorator:
    def __init__(self, component):
        self._component = component

    def operation(self):
        print('before')
        return self._component.operation()
"""

DECORATOR_WRAPPED = """\
class CachingWrapper:
    def __init__(self, wrapped):
        self._wrapped = wrapped
"""


def test_decorator_class_name():
    findings = DecoratorPatternDetector().detect(DECORATOR_CLASS_CODE, "python")
    assert len(findings) == 1
    assert findings[0].name == "decorator"
    assert "Decorator" in (findings[0].details or "")


def test_decorator_wrapped_field():
    findings = DecoratorPatternDetector().detect(DECORATOR_WRAPPED, "python")
    assert len(findings) == 1
    assert findings[0].name == "decorator"
    assert "_wrapped" in (findings[0].details or "")


def test_decorator_no_match():
    assert DecoratorPatternDetector().detect("def foo(): pass", "python") == []


# ---------------------------------------------------------------------------
# FacadeDetector
# ---------------------------------------------------------------------------

FACADE_CODE = """\
class HomeTheaterFacade:
    def watch_movie(self): ...
    def end_movie(self): ...
"""


def test_facade_detects():
    findings = FacadeDetector().detect(FACADE_CODE, "python")
    assert len(findings) == 1
    assert findings[0].name == "facade"
    assert findings[0].location is not None


def test_facade_no_match():
    assert FacadeDetector().detect("class Foo: pass", "python") == []


# ---------------------------------------------------------------------------
# ProxyDetector
# ---------------------------------------------------------------------------

PROXY_CODE = """\
class ImageProxy:
    def __init__(self, filename):
        self._real = None
        self._filename = filename

    def display(self):
        if self._real is None:
            self._real = RealImage(self._filename)
        self._real.display()
"""


def test_proxy_detects():
    findings = ProxyDetector().detect(PROXY_CODE, "python")
    assert len(findings) == 1
    assert findings[0].name == "proxy"
    assert findings[0].location is not None


def test_proxy_no_match():
    assert ProxyDetector().detect("class Foo: pass", "python") == []


# ---------------------------------------------------------------------------
# StrategyDetector
# ---------------------------------------------------------------------------

STRATEGY_SETTER = """\
class Sorter:
    def set_strategy(self, strategy):
        self._strategy = strategy

    def sort(self, data):
        return self._strategy.sort(data)
"""

STRATEGY_FIELD = """\
class Navigator:
    def __init__(self):
        self._strategy = WalkingStrategy()
"""


def test_strategy_setter():
    findings = StrategyDetector().detect(STRATEGY_SETTER, "python")
    assert len(findings) == 1
    assert findings[0].name == "strategy"
    assert "set_strategy" in (findings[0].details or "")


def test_strategy_field():
    findings = StrategyDetector().detect(STRATEGY_FIELD, "python")
    assert len(findings) == 1
    assert findings[0].name == "strategy"
    assert "_strategy" in (findings[0].details or "")


def test_strategy_no_match():
    assert StrategyDetector().detect("def foo(): pass", "python") == []


# ---------------------------------------------------------------------------
# CompositeDetector
# ---------------------------------------------------------------------------

COMPOSITE_CODE = """\
class FileSystem:
    def __init__(self):
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def remove_child(self, child):
        self.children.remove(child)
"""

COMPOSITE_CHILDREN_ONLY = """\
class Tree:
    def __init__(self):
        self.children = []

    def add_child(self, node):
        self.children.append(node)
"""


def test_composite_full():
    findings = CompositeDetector().detect(COMPOSITE_CODE, "python")
    assert len(findings) == 1
    assert findings[0].name == "composite"
    assert "remove_child" in (findings[0].details or "")


def test_composite_with_children_collection():
    findings = CompositeDetector().detect(COMPOSITE_CHILDREN_ONLY, "python")
    assert len(findings) == 1
    assert findings[0].name == "composite"


def test_composite_no_add_child():
    assert CompositeDetector().detect("self.children = []", "python") == []


def test_composite_add_without_collection():
    assert CompositeDetector().detect("def add_child(self, c): pass", "python") == []


# ---------------------------------------------------------------------------
# ChainOfResponsibilityDetector
# ---------------------------------------------------------------------------

CHAIN_CODE = """\
class Handler:
    def set_next(self, handler):
        self._next = handler
        return handler

    def handle(self, request):
        if self._next:
            return self._next.handle(request)
        return None
"""


def test_chain_detects():
    findings = ChainOfResponsibilityDetector().detect(CHAIN_CODE, "python")
    assert len(findings) == 1
    assert findings[0].name == "chain_of_responsibility"
    assert findings[0].location is not None


def test_chain_set_next_only():
    assert (
        ChainOfResponsibilityDetector().detect("def set_next(self, h): pass", "python")
        == []
    )


def test_chain_handle_only():
    assert (
        ChainOfResponsibilityDetector().detect("def handle(self, r): pass", "python")
        == []
    )


# ---------------------------------------------------------------------------
# IteratorDetector
# ---------------------------------------------------------------------------

ITERATOR_DUNDER = """\
class NumberRange:
    def __init__(self, start, end):
        self._current = start
        self._end = end

    def __iter__(self):
        return self

    def __next__(self):
        if self._current >= self._end:
            raise StopIteration
        val = self._current
        self._current += 1
        return val
"""

ITERATOR_HAS_NEXT = """\
class ListIterator:
    def has_next(self):
        return self._pos < len(self._items)

    def next(self):
        item = self._items[self._pos]
        self._pos += 1
        return item
"""

ITERATOR_GO = """\
type Iterator interface {
    HasNext() bool
    Next() interface{}
}
"""


def test_iterator_dunder_protocol():
    findings = IteratorDetector().detect(ITERATOR_DUNDER, "python")
    assert len(findings) == 1
    assert findings[0].name == "iterator"
    assert "__iter__" in (findings[0].details or "")


def test_iterator_has_next_api():
    findings = IteratorDetector().detect(ITERATOR_HAS_NEXT, "python")
    assert len(findings) == 1
    assert findings[0].name == "iterator"
    assert "has_next" in (findings[0].details or "")


def test_iterator_go_interface():
    findings = IteratorDetector().detect(ITERATOR_GO, "go")
    assert len(findings) == 1
    assert findings[0].name == "iterator"


def test_iterator_no_match():
    assert IteratorDetector().detect("def foo(): pass", "python") == []


def test_iterator_iter_without_next():
    assert IteratorDetector().detect("def __iter__(self): return self", "python") == []
