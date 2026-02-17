"""Python zen principles as Pydantic models."""

from pydantic import HttpUrl

from ...rules.base_models import LanguageZenPrinciples, PrincipleCategory, ZenPrinciple

PYTHON_ZEN = LanguageZenPrinciples(
    language="python",
    name="Python",
    philosophy="The Zen of Python (PEP 20)",
    source_text="PEP 20 - The Zen of Python",
    source_url=HttpUrl("https://peps.python.org/pep-0020/"),
    principles=[
        ZenPrinciple(
            id="python-001",
            principle="Beautiful is better than ugly",
            category=PrincipleCategory.READABILITY,
            severity=4,
            description="Code should be aesthetically pleasing and well-formatted",
            violations=[
                "Inconsistent indentation",
                "Poor naming conventions",
                "Lack of whitespace around operators",
                "Overly compact code",
            ],
            metrics={
                "max_line_length": 88,
                "naming_convention": "snake_case",
                "min_identifier_length": 2,
            },
        ),
        ZenPrinciple(
            id="python-002",
            principle="Explicit is better than implicit",
            category=PrincipleCategory.CLARITY,
            severity=7,
            description="Code behavior should be obvious and unambiguous",
            violations=[
                "Using global variables without declaration",
                "Implicit type conversions",
                "Magic numbers without constants",
                "Overuse of * imports",
                "Hidden side effects in functions",
            ],
            detectable_patterns=[
                "from module import *",
                "global keyword abuse",
                "functions modifying arguments without clear indication",
            ],
        ),
        ZenPrinciple(
            id="python-003",
            principle="Simple is better than complex",
            category=PrincipleCategory.COMPLEXITY,
            severity=8,
            description="Favor straightforward solutions over complicated ones",
            violations=[
                "High cyclomatic complexity (>10)",
                "Overly nested comprehensions",
                "Unnecessary abstraction layers",
                "Complex one-liners",
            ],
            metrics={
                "max_cyclomatic_complexity": 10,
            },
        ),
        ZenPrinciple(
            id="python-004",
            principle="Complex is better than complicated",
            category=PrincipleCategory.ARCHITECTURE,
            severity=7,
            description="When complexity is necessary, keep it organized and understandable",
            violations=[
                "Tangled dependencies",
                "Unclear module boundaries",
                "Mixed concerns in single class",
            ],
        ),
        ZenPrinciple(
            id="python-005",
            principle="Flat is better than nested",
            category=PrincipleCategory.STRUCTURE,
            severity=8,
            description="Avoid deep nesting of control structures",
            violations=[
                "Nesting depth > 3 levels",
                "Multiple nested loops",
                "Deeply nested if-else chains",
            ],
            metrics={"max_nesting_depth": 3},
        ),
        ZenPrinciple(
            id="python-006",
            principle="Sparse is better than dense",
            category=PrincipleCategory.READABILITY,
            severity=5,
            description="Code should have appropriate spacing and not be cramped",
            violations=[
                "Multiple statements on one line",
                "Overly compact expressions",
                "Lack of blank lines between logical sections",
            ],
            metrics={
                "max_statements_per_line": 1,
                "min_blank_lines_between_defs": 1,
            },
        ),
        ZenPrinciple(
            id="python-007",
            principle="Readability counts",
            category=PrincipleCategory.READABILITY,
            severity=9,
            description="Code is read more often than written",
            violations=[
                "Functions longer than 50 lines",
                "Classes longer than 300 lines",
                "Unclear variable names (a, b, x)",
                "Missing docstrings for public APIs",
            ],
            metrics={"max_function_length": 50, "max_class_length": 300},
        ),
        ZenPrinciple(
            id="python-008",
            principle="Special cases aren't special enough to break the rules",
            category=PrincipleCategory.CONSISTENCY,
            severity=6,
            description="Maintain consistency even for edge cases",
            violations=[
                "Inconsistent error handling patterns",
                "Different naming conventions within same module",
                "Special-case code paths without justification",
            ],
            metrics={
                "max_naming_styles": 1,
            },
        ),
        ZenPrinciple(
            id="python-009",
            principle="Errors should never pass silently",
            category=PrincipleCategory.ERROR_HANDLING,
            severity=9,
            description="Always handle errors explicitly",
            violations=[
                "Bare except clauses",
                "Catching Exception without handling",
                "Ignoring return codes",
                "Empty except blocks",
            ],
            detectable_patterns=["except: pass", "except Exception: pass"],
        ),
        ZenPrinciple(
            id="python-010",
            principle="In the face of ambiguity, refuse the temptation to guess",
            category=PrincipleCategory.CORRECTNESS,
            severity=7,
            description="Be explicit rather than making assumptions",
            violations=[
                "Implicit type assumptions",
                "Unclear function contracts",
                "Missing input validation",
            ],
            metrics={
                "require_type_hints": True,
            },
        ),
        ZenPrinciple(
            id="python-011",
            principle="There should be one-- and preferably only one --obvious way to do it",
            category=PrincipleCategory.IDIOMS,
            severity=6,
            description="Prefer pythonic idioms over alternatives",
            violations=[
                "Using range(len()) instead of enumerate",
                "Manual iteration instead of list comprehensions",
                "Not using context managers for resources",
                "Multiple implementations of same logic",
            ],
            detectable_patterns=[
                "for i in range(len(list))",
                "file without 'with' statement",
            ],
        ),
        ZenPrinciple(
            id="python-012",
            principle="Namespaces are one honking great idea",
            category=PrincipleCategory.ORGANIZATION,
            severity=7,
            description="Use namespaces to organize code clearly",
            violations=[
                "Polluting global namespace",
                "Too many items in __all__",
                "Deep module nesting without purpose",
            ],
            metrics={
                "max_top_level_symbols": 25,
                "max_exports": 20,
            },
        ),
    ],
)
