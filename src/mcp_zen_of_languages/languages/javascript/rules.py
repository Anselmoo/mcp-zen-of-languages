"""JavaScript zen principles as Pydantic models."""

from pydantic import HttpUrl

from mcp_zen_of_languages.rules.base_models import LanguageZenPrinciples
from mcp_zen_of_languages.rules.base_models import PrincipleCategory
from mcp_zen_of_languages.rules.base_models import ZenPrinciple


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
        ZenPrinciple(
            id="js-012",
            principle="Use destructuring for assignment",
            category=PrincipleCategory.IDIOMS,
            severity=5,
            description=(
                "Prefer destructuring over manually extracting "
                "object properties or array elements"
            ),
            violations=[
                "Consecutive property extractions from same object",
                "Repetitive array index access (arr[0], arr[1])",
                "Repeated parameter property access",
            ],
            source_url=HttpUrl("https://github.com/airbnb/javascript#destructuring"),
        ),
        ZenPrinciple(
            id="js-013",
            principle="Use object spread over Object.assign",
            category=PrincipleCategory.IDIOMS,
            severity=5,
            description=(
                "Prefer the spread syntax ({...obj}) over "
                "Object.assign for shallow cloning and merging"
            ),
            violations=[
                "Object.assign with empty first argument",
                "Object.assign for shallow cloning",
                "Object.assign with 3+ arguments when spread is clearer",
            ],
            source_url=HttpUrl(
                "https://github.com/airbnb/javascript#objects--rest-spread"
            ),
        ),
        ZenPrinciple(
            id="js-014",
            principle="Avoid with statement",
            category=PrincipleCategory.CORRECTNESS,
            severity=9,
            description=(
                "The with statement is disallowed in strict mode "
                "and creates ambiguous scope resolution"
            ),
            violations=[
                "Any usage of with statement",
            ],
            source_url=HttpUrl(
                "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/with"
            ),
        ),
        ZenPrinciple(
            id="js-015",
            principle="Limit function parameter count",
            category=PrincipleCategory.DESIGN,
            severity=7,
            description=(
                "Functions with too many positional parameters "
                "should accept an options object instead"
            ),
            violations=[
                "Functions with more than 3 positional parameters",
                "Constructor functions with more than 4 parameters",
            ],
            metrics={"max_params": 3},
            source_url=HttpUrl(
                "https://github.com/airbnb/javascript#functions--defaults-last"
            ),
        ),
        ZenPrinciple(
            id="js-016",
            principle="No eval()",
            category=PrincipleCategory.SECURITY,
            severity=9,
            description=(
                "Use of eval() introduces security vulnerabilities "
                "and prevents JavaScript engine optimizations"
            ),
            violations=[
                "Direct eval() calls",
                "new Function() constructor",
                "setTimeout or setInterval with string arguments",
            ],
            source_url=HttpUrl("https://github.com/airbnb/javascript#properties--eval"),
        ),
        ZenPrinciple(
            id="js-017",
            principle="Prefer Array.from/spread over arguments",
            category=PrincipleCategory.IDIOMS,
            severity=6,
            description=(
                "The arguments object is a legacy non-array; "
                "use rest parameters (...args) instead"
            ),
            violations=[
                "Direct use of arguments keyword",
                "Array.prototype.slice.call(arguments)",
                "Array.from(arguments)",
            ],
            recommended_alternative="Rest parameters (...args)",
            source_url=HttpUrl(
                "https://github.com/airbnb/javascript#functions--arguments-shadow"
            ),
        ),
        ZenPrinciple(
            id="js-018",
            principle="No prototype mutation on built-in objects",
            category=PrincipleCategory.ARCHITECTURE,
            severity=9,
            description=(
                "Extending native prototypes creates global side effects "
                "and can break third-party code"
            ),
            violations=[
                "Array.prototype modification",
                "String.prototype modification",
                "Object.prototype modification",
                "Function.prototype modification",
            ],
            source_url=HttpUrl(
                "https://github.com/airbnb/javascript"
                "#native-prototypes--no-extend-native"
            ),
        ),
    ],
)
