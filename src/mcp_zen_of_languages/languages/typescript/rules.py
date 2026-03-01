"""TypeScript zen principles as Pydantic models."""

from pydantic import HttpUrl

from mcp_zen_of_languages.rules.base_models import LanguageZenPrinciples
from mcp_zen_of_languages.rules.base_models import PrincipleCategory
from mcp_zen_of_languages.rules.base_models import ZenPrinciple


TYPESCRIPT_ZEN = LanguageZenPrinciples(
    language="typescript",
    name="TypeScript",
    philosophy="Type Safety and Maintainability",
    source_text="Google TypeScript Style Guide",
    source_url=HttpUrl("https://google.github.io/styleguide/tsguide.html"),
    principles=[
        ZenPrinciple(
            id="ts-001",
            principle="Avoid 'any' type",
            category=PrincipleCategory.TYPE_SAFETY,
            severity=9,
            description="Use proper types instead of any to maintain type safety",
            violations=[
                "Explicit any annotations",
                "Implicit any from missing types",
                "Type assertions to any",
                "any[] arrays",
            ],
            detectable_patterns=[": any", "as any"],
            recommended_alternative="unknown, specific types, or generics",
            metrics={
                "max_any_usages": 0,
                "detect_explicit_any": True,
                "detect_assertions_any": True,
                "detect_any_arrays": True,
            },
        ),
        ZenPrinciple(
            id="ts-002",
            principle="Use strict mode",
            category=PrincipleCategory.CONFIGURATION,
            severity=9,
            description="Enable strict TypeScript compiler options",
            violations=[
                "strict: false in tsconfig",
                "Disabled strictNullChecks",
                "Disabled noImplicitAny",
            ],
            required_config={
                "strict": True,
                "noImplicitAny": True,
                "strictNullChecks": True,
            },
            metrics={
                "require_strict": True,
                "require_no_implicit_any": True,
                "require_strict_null_checks": True,
            },
        ),
        ZenPrinciple(
            id="ts-003",
            principle="Prefer interfaces over type aliases for objects",
            category=PrincipleCategory.IDIOMS,
            severity=5,
            description="Use interfaces for object shapes, types for unions/primitives",
            violations=[
                "Type aliases for simple object shapes",
                "Not using interface extension",
            ],
            detectable_patterns=["type ObjectShape = { ... }"],
            metrics={
                "max_object_type_aliases": 0,
            },
        ),
        ZenPrinciple(
            id="ts-004",
            principle="Always specify return types",
            category=PrincipleCategory.TYPE_SAFETY,
            severity=7,
            description="Explicit return types improve readability and catch errors",
            violations=[
                "Public functions without return type",
                "Exported functions without return type",
                "Callbacks without return type",
            ],
            metrics={
                "require_return_types": True,
            },
        ),
        ZenPrinciple(
            id="ts-005",
            principle="Use readonly when appropriate",
            category=PrincipleCategory.IMMUTABILITY,
            severity=6,
            description="Mark immutable properties as readonly",
            violations=[
                "Properties that should be readonly",
                "Arrays that should be ReadonlyArray",
                "Mutable config objects",
            ],
            metrics={
                "require_readonly_properties": True,
                "min_readonly_occurrences": 1,
            },
        ),
        ZenPrinciple(
            id="ts-006",
            principle="Leverage type guards",
            category=PrincipleCategory.TYPE_SAFETY,
            severity=7,
            description="Use type guards for runtime type checking",
            violations=[
                "Type assertions without validation",
                "Not narrowing union types",
                "Using 'as' instead of type guards",
            ],
            recommended_alternative="User-defined type guards (is predicates)",
            metrics={
                "max_type_assertions": 0,
            },
        ),
        ZenPrinciple(
            id="ts-007",
            principle="Use utility types",
            category=PrincipleCategory.IDIOMS,
            severity=6,
            description="Leverage built-in utility types (Partial, Pick, Omit, etc.)",
            violations=[
                "Manual type transformations",
                "Duplicated type definitions",
                "Not using Partial for optional updates",
            ],
            metrics={
                "min_utility_type_usage": 1,
                "min_object_type_aliases": 2,
            },
        ),
        ZenPrinciple(
            id="ts-008",
            principle="Avoid non-null assertions",
            category=PrincipleCategory.TYPE_SAFETY,
            severity=8,
            description="Handle null/undefined properly instead of using !",
            violations=[
                "Excessive use of ! operator",
                "Non-null assertions without validation",
                "Chained non-null assertions",
            ],
            detectable_patterns=["variable!", "?.!"],
            metrics={
                "max_non_null_assertions": 0,
            },
        ),
        ZenPrinciple(
            id="ts-009",
            principle="Use enums or const assertions appropriately",
            category=PrincipleCategory.IDIOMS,
            severity=6,
            description="Use const enums or const assertions for constant values",
            violations=[
                "Plain objects for enumerations",
                "String literal unions without const assertion",
                "Regular enums that should be const",
            ],
            metrics={
                "max_plain_enum_objects": 0,
            },
        ),
        ZenPrinciple(
            id="ts-010",
            principle="Prefer unknown over any for uncertain types",
            category=PrincipleCategory.TYPE_SAFETY,
            severity=7,
            description="Use unknown when type is truly unknown, forces type checking",
            violations=[
                "Using any for API responses",
                "Using any for error types",
                "any for third-party data",
            ],
            metrics={
                "max_any_for_unknown": 0,
            },
        ),
        ZenPrinciple(
            id="ts-011",
            principle="Use optional chaining instead of manual null checks",
            category=PrincipleCategory.IDIOMS,
            severity=5,
            description="Optional chaining (?.) simplifies nested property access and avoids verbose guard clauses",
            violations=[
                "Manual && chains for nested access",
                "Verbose null/undefined checks before property access",
                "Nested ternaries for safe property access",
            ],
            metrics={
                "max_manual_null_checks": 0,
            },
        ),
        ZenPrinciple(
            id="ts-012",
            principle="Prefer for-of and array methods over index loops",
            category=PrincipleCategory.IDIOMS,
            severity=4,
            description="Modern iteration is more readable and less error-prone than C-style for loops",
            violations=[
                "Using for(let i=0; ...) when for-of suffices",
                "Index-based iteration over arrays",
                "Manual length-based loops",
            ],
            metrics={
                "max_index_loops": 0,
            },
        ),
        ZenPrinciple(
            id="ts-013",
            principle="Prefer async/await over raw promise chains",
            category=PrincipleCategory.ASYNC,
            severity=6,
            description="async/await produces flatter, more readable asynchronous code than .then() chains",
            violations=[
                "Using .then() chains instead of await",
                "Nested .then() callbacks",
                "Mixing .then() and async/await styles",
            ],
            metrics={
                "max_promise_chains": 0,
            },
        ),
        ZenPrinciple(
            id="ts-014",
            principle="Prefer named exports over default exports",
            category=PrincipleCategory.ORGANIZATION,
            severity=4,
            description="Named exports improve refactoring support and IDE auto-imports",
            violations=[
                "Using export default for modules",
                "Default-exporting classes or functions",
                "Inconsistent export styles in a project",
            ],
            metrics={
                "max_default_exports": 0,
            },
        ),
        ZenPrinciple(
            id="ts-015",
            principle="Avoid catch-all types like Object or {}",
            category=PrincipleCategory.TYPE_SAFETY,
            severity=6,
            description="Catch-all types bypass the type system; use precise types or Record instead",
            violations=[
                "Typing as Object or object",
                "Using {} as a type annotation",
                "Overly broad type parameters",
            ],
            metrics={
                "max_catch_all_types": 0,
            },
        ),
        ZenPrinciple(
            id="ts-016",
            principle="Avoid console usage in production code",
            category=PrincipleCategory.CLARITY,
            severity=4,
            description="Use a structured logging framework instead of console.log for production code",
            violations=[
                "console.log for debugging left in code",
                "console.error instead of proper error handling",
                "console.warn without structured logging",
            ],
            metrics={
                "max_console_usages": 0,
            },
        ),
        ZenPrinciple(
            id="ts-017",
            principle="Use ES module imports instead of require()",
            category=PrincipleCategory.IDIOMS,
            severity=5,
            description="ES module syntax enables tree-shaking and static analysis",
            violations=[
                "Using require() in TypeScript files",
                "Mixing require and import styles",
                "CommonJS patterns in modern TypeScript",
            ],
            metrics={
                "max_require_calls": 0,
            },
        ),
        ZenPrinciple(
            id="ts-018",
            principle="Use template literals instead of string concatenation",
            category=PrincipleCategory.READABILITY,
            severity=3,
            description="Template literals are more readable and less error-prone than + concatenation",
            violations=[
                "String concatenation with + operator",
                "Multi-part string building with +",
                "Variable interpolation via concatenation",
            ],
            metrics={
                "max_string_concats": 0,
            },
        ),
    ],
)
