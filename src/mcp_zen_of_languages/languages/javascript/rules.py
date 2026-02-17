"""JavaScript zen principles as Pydantic models."""

from pydantic import HttpUrl

from ...rules.base_models import LanguageZenPrinciples, PrincipleCategory, ZenPrinciple

JAVASCRIPT_ZEN = LanguageZenPrinciples(
    language="javascript",
    name="JavaScript",
    philosophy="Modern JavaScript Best Practices",
    source_text="Airbnb JavaScript Style Guide",
    source_url=HttpUrl("https://github.com/airbnb/javascript"),
    principles=[
        ZenPrinciple(
            id="js-001",
            principle="Avoid callback hell",
            category=PrincipleCategory.ASYNC,
            severity=8,
            description="Use modern async patterns instead of nested callbacks",
            violations=[
                "Nested callbacks > 2 levels",
                "Pyramid of doom pattern",
                "Not using async/await when available",
            ],
            metrics={"max_callback_nesting": 2},
            recommended_alternative="async/await or Promises",
        ),
        ZenPrinciple(
            id="js-002",
            principle="Prefer const over let, never var",
            category=PrincipleCategory.IMMUTABILITY,
            severity=7,
            description="Use const by default for immutability",
            violations=[
                "Using var keyword",
                "Using let for values that don't change",
                "Reassigning const-eligible variables",
            ],
            detectable_patterns=["var keyword usage", "let without reassignment"],
        ),
        ZenPrinciple(
            id="js-003",
            principle="Use strict equality",
            category=PrincipleCategory.CORRECTNESS,
            severity=8,
            description="Always use === and !== to avoid type coercion bugs",
            violations=[
                "Using == or !=",
                "Relying on truthy/falsy in critical comparisons",
            ],
            detectable_patterns=["== comparison", "!= comparison"],
        ),
        ZenPrinciple(
            id="js-004",
            principle="Avoid global state",
            category=PrincipleCategory.ARCHITECTURE,
            severity=9,
            description="Minimize global variables and shared mutable state",
            violations=[
                "Global variable declarations",
                "Window object pollution",
                "Singleton pattern overuse",
                "Shared mutable state",
            ],
            detectable_patterns=["window.", "globalThis.", "global."],
        ),
        ZenPrinciple(
            id="js-005",
            principle="Functions should do one thing",
            category=PrincipleCategory.DESIGN,
            severity=7,
            description="Single Responsibility Principle for functions",
            violations=[
                "Functions > 50 lines",
                "Functions with multiple side effects",
                "Functions that both compute and mutate",
            ],
            metrics={"max_function_length": 50, "max_parameters": 3},
        ),
        ZenPrinciple(
            id="js-006",
            principle="Use modern ES6+ features",
            category=PrincipleCategory.IDIOMS,
            severity=6,
            description="Leverage destructuring, arrow functions, template literals",
            violations=[
                "String concatenation instead of template literals",
                "Function expressions instead of arrow functions",
                "Manual object property access instead of destructuring",
                "Not using spread operator",
            ],
            detectable_patterns=[
                "function() instead of () =>",
                "string + variable instead of template literal",
            ],
        ),
        ZenPrinciple(
            id="js-007",
            principle="Handle errors explicitly",
            category=PrincipleCategory.ERROR_HANDLING,
            severity=9,
            description="Always handle promise rejections and errors",
            violations=[
                "Promises without .catch()",
                "async functions without try-catch",
                "Ignoring error callbacks",
                "Swallowing errors silently",
            ],
            detectable_patterns=["Promise without catch", "async without try-catch"],
        ),
        ZenPrinciple(
            id="js-008",
            principle="Avoid magic numbers and strings",
            category=PrincipleCategory.CLARITY,
            severity=6,
            description="Use named constants for literal values",
            violations=[
                "Hardcoded numbers with unclear meaning",
                "String literals repeated multiple times",
                "Configuration values inline",
            ],
            detectable_patterns=[" = 0", " = 1"],
        ),
        ZenPrinciple(
            id="js-009",
            principle="Prefer composition over inheritance",
            category=PrincipleCategory.ARCHITECTURE,
            severity=7,
            description=(
                "Use object composition and mixins instead of deep class hierarchies"
            ),
            violations=[
                "Inheritance chains > 2 levels",
                "Overuse of class inheritance",
                "Not using composition patterns",
            ],
            metrics={"max_inheritance_depth": 2},
        ),
        ZenPrinciple(
            id="js-010",
            principle="Keep functions pure when possible",
            category=PrincipleCategory.FUNCTIONAL,
            severity=6,
            description="Minimize side effects and favor pure functions",
            violations=[
                "Functions modifying external state",
                "Functions with hidden side effects",
                "Impure array methods (push, splice) when map/filter would work",
            ],
            detectable_patterns=["push(", "splice("],
        ),
        ZenPrinciple(
            id="js-011",
            principle="Use meaningful names",
            category=PrincipleCategory.READABILITY,
            severity=8,
            description="Variable and function names should clearly express intent",
            violations=[
                "Single letter variables (except loop counters)",
                "Abbreviations without context",
                "Generic names (data, value, temp)",
                "Misleading names",
            ],
            metrics={"min_identifier_length": 2},
        ),
    ],
)
