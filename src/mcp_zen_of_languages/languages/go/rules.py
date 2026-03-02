"""Go zen principles as Pydantic models."""

from pydantic import HttpUrl

from mcp_zen_of_languages.rules.base_models import LanguageZenPrinciples
from mcp_zen_of_languages.rules.base_models import PrincipleCategory
from mcp_zen_of_languages.rules.base_models import ZenPrinciple


GO_ZEN = LanguageZenPrinciples(
    language="go",
    name="Go",
    philosophy="Simplicity, Clarity, and Pragmatism",
    source_text="Effective Go & The Zen of Go",
    source_url=HttpUrl("https://the-zen-of-go.netlify.app/"),
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
                "Plural package names (utils \u2192 util)",
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
        ZenPrinciple(
            id="go-013",
            principle="Organize by responsibility",
            category=PrincipleCategory.ORGANIZATION,
            severity=6,
            description=("Group code by domain responsibility, not by technical layer"),
            violations=[
                "Organizing packages by type (models/, controllers/)",
                "Deeply nested package hierarchies",
                "Circular package dependencies",
                "Package names reflecting technical role instead of domain",
            ],
            detectable_patterns=["package models", "package controllers"],
        ),
        ZenPrinciple(
            id="go-014",
            principle="Embed for composition, not inheritance",
            category=PrincipleCategory.STRUCTURE,
            severity=7,
            description=(
                "Use struct embedding for composing behaviors, "
                "not faking OOP inheritance"
            ),
            violations=[
                "Deep embedding chains exceeding two levels",
                "Embedding structs solely to access their fields",
                "Name collisions from overlapping embedded methods",
            ],
            detectable_patterns=["type Foo struct { Bar"],
            metrics={"max_embedding_depth": 2},
        ),
        ZenPrinciple(
            id="go-015",
            principle="Communicate by sharing memory through channels",
            category=PrincipleCategory.CONCURRENCY,
            severity=8,
            description=(
                "Prefer channels over shared-memory synchronization primitives"
            ),
            violations=[
                "Using sync.Mutex where a channel would be clearer",
                "Shared mutable state accessed by multiple goroutines",
                "Missing synchronization around concurrent map access",
            ],
            detectable_patterns=["sync.Mutex", "sync.RWMutex"],
        ),
        ZenPrinciple(
            id="go-016",
            principle="Avoid unnecessary complexity",
            category=PrincipleCategory.COMPLEXITY,
            severity=7,
            description=(
                "Prefer straightforward solutions; complexity must be justified"
            ),
            violations=[
                "Deeply nested control flow exceeding three levels",
                "Functions longer than 50 lines",
                "Cyclomatic complexity above 10 per function",
            ],
            metrics={"max_nesting_depth": 3, "max_function_lines": 50},
        ),
        ZenPrinciple(
            id="go-017",
            principle="Handle every error path",
            category=PrincipleCategory.CORRECTNESS,
            severity=9,
            description=(
                "Ensure all error branches are explicitly handled, "
                "not just the happy path"
            ),
            violations=[
                "Returning early without wrapping or annotating the error",
                "Silently swallowing errors inside deferred calls",
                "Using log.Fatal in library code instead of returning an error",
            ],
        ),
        ZenPrinciple(
            id="go-018",
            principle="Avoid premature optimization",
            category=PrincipleCategory.PERFORMANCE,
            severity=5,
            description=(
                "Write clear code first; optimize only after "
                "profiling proves a bottleneck"
            ),
            violations=[
                "Unsafe pointer tricks without benchmark justification",
                "Manual memory pooling where sync.Pool is not warranted",
                "Replacing readable code with micro-optimizations "
                "lacking profiling data",
            ],
        ),
        ZenPrinciple(
            id="go-019",
            principle="Design for testability",
            category=PrincipleCategory.DESIGN,
            severity=7,
            description=(
                "Structure code so that dependencies can be replaced in tests"
            ),
            violations=[
                "Hard-coded external service calls with no interface seam",
                "Global state that prevents parallel test execution",
                "Unexported helpers that duplicate test setup across packages",
            ],
        ),
        ZenPrinciple(
            id="go-020",
            principle="Write self-documenting code",
            category=PrincipleCategory.READABILITY,
            severity=5,
            description=(
                "Let clear naming and structure replace the need for most comments"
            ),
            violations=[
                "Comments that restate the code instead of explaining intent",
                "Exported symbols missing GoDoc-style comments",
                "Magic numbers without named constants",
            ],
        ),
    ],
)
