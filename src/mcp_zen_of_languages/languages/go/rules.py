"""Go zen principles as Pydantic models."""

from pydantic import HttpUrl

from ...rules.base_models import LanguageZenPrinciples, PrincipleCategory, ZenPrinciple

GO_ZEN = LanguageZenPrinciples(
    language="go",
    name="Go",
    philosophy="Simplicity, Clarity, and Pragmatism",
    source_text="Effective Go",
    source_url=HttpUrl("https://go.dev/doc/effective_go"),
    principles=[
        ZenPrinciple(
            id="go-001",
            principle="Errors are values",
            category=PrincipleCategory.ERROR_HANDLING,
            severity=9,
            description="Handle errors explicitly, don't panic",
            violations=[
                "Ignoring error returns",
                "_ assignment for errors",
                "Excessive panic usage",
                "Not checking error != nil",
            ],
            detectable_patterns=["_, err := without checking", "panic() in libraries"],
        ),
        ZenPrinciple(
            id="go-002",
            principle="Accept interfaces, return structs",
            category=PrincipleCategory.DESIGN,
            severity=7,
            description=(
                "Function parameters should be interfaces, returns concrete types"
            ),
            violations=[
                "Returning interfaces from functions",
                "Accepting concrete types when interface would work",
                "Premature interface abstraction",
            ],
            detectable_patterns=["interface{"],
        ),
        ZenPrinciple(
            id="go-003",
            principle="Make the zero value useful",
            category=PrincipleCategory.DESIGN,
            severity=6,
            description="Structs should be usable without explicit initialization",
            violations=[
                "Structs requiring explicit initialization",
                "Mandatory constructor functions",
                "Unusable zero values",
            ],
            detectable_patterns=["func New"],
        ),
        ZenPrinciple(
            id="go-004",
            principle="Use short variable names",
            category=PrincipleCategory.READABILITY,
            severity=5,
            description="Prefer short, contextual names in limited scopes",
            violations=[
                "Long variable names in small scopes",
                "unnecessarilyLongVariableNames",
                "Unclear abbreviations in large scopes",
            ],
        ),
        ZenPrinciple(
            id="go-005",
            principle="Don't use pointer to interface",
            category=PrincipleCategory.DESIGN,
            severity=8,
            description="Interfaces are already pointers, don't add *",
            violations=[
                "*Interface type parameters",
                "Pointer to interface return types",
            ],
            detectable_patterns=["*io.Reader", "*SomeInterface"],
        ),
        ZenPrinciple(
            id="go-006",
            principle="Avoid goroutine leaks",
            category=PrincipleCategory.CONCURRENCY,
            severity=9,
            description="Always ensure goroutines can terminate",
            violations=[
                "Goroutines without cancellation",
                "Channels without close",
                "Infinite loops in goroutines",
                "No context for cancellation",
            ],
            detectable_patterns=["go func"],
        ),
        ZenPrinciple(
            id="go-007",
            principle="Use defer for cleanup",
            category=PrincipleCategory.IDIOMS,
            severity=7,
            description="Defer resource cleanup immediately after acquisition",
            violations=[
                "Manual cleanup scattered in code",
                "Not using defer for file.Close()",
                "Not deferring mutex.Unlock()",
            ],
        ),
        ZenPrinciple(
            id="go-008",
            principle="Package names are singular",
            category=PrincipleCategory.ORGANIZATION,
            severity=5,
            description="Package names should be lowercase, singular nouns",
            violations=[
                "Plural package names (utils → util)",
                "CamelCase package names",
                "Underscores in package names",
            ],
            detectable_patterns=["package utils", "package helpers"],
        ),
        ZenPrinciple(
            id="go-009",
            principle="Avoid package-level state",
            category=PrincipleCategory.ARCHITECTURE,
            severity=7,
            description="Minimize global variables and package-level mutable state",
            violations=[
                "Mutable package-level variables",
                "Package init() with side effects",
                "Global singletons",
            ],
            detectable_patterns=["var "],
        ),
        ZenPrinciple(
            id="go-010",
            principle="Keep interfaces small",
            category=PrincipleCategory.DESIGN,
            severity=7,
            description="Prefer many small interfaces over large ones",
            violations=[
                "Interfaces with > 3 methods",
                "God interfaces",
                "Interface segregation violations",
            ],
            metrics={"max_interface_methods": 3},
        ),
        ZenPrinciple(
            id="go-011",
            principle="Use context for cancellation",
            category=PrincipleCategory.CONCURRENCY,
            severity=8,
            description="Pass context.Context for cancellation and deadlines",
            violations=[
                "Long-running functions without context",
                "HTTP handlers without request context",
                "Not propagating context",
            ],
        ),
        ZenPrinciple(
            id="go-012",
            principle="Avoid init() when possible",
            category=PrincipleCategory.INITIALIZATION,
            severity=6,
            description="Prefer explicit initialization over init()",
            violations=[
                "Complex logic in init()",
                "Multiple init() functions",
                "Side effects in init()",
            ],
            detectable_patterns=["func init("],
        ),
    ],
)
