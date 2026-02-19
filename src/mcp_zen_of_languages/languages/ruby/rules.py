"""Ruby zen principles as Pydantic models."""

from pydantic import HttpUrl

from mcp_zen_of_languages.rules.base_models import (
    LanguageZenPrinciples,
    PrincipleCategory,
    ZenPrinciple,
)

RUBY_ZEN = LanguageZenPrinciples(
    language="ruby",
    name="Ruby",
    philosophy="Principle of Least Surprise (POLS) and Developer Happiness",
    source_text="Ruby Style Guide",
    source_url=HttpUrl("https://rubystyle.guide/"),
    principles=[
        ZenPrinciple(
            id="ruby-001",
            principle="Convention over configuration",
            category=PrincipleCategory.IDIOMS,
            severity=7,
            description="Follow Ruby naming and structural conventions",
            violations=[
                "camelCase instead of snake_case",
                "Non-standard class naming",
                "CONSTANTS in lowercase",
                "Methods starting with capital letters",
            ],
            metrics={
                "naming_convention": "snake_case for methods/variables, PascalCase for classes",
            },
        ),
        ZenPrinciple(
            id="ruby-002",
            principle="DRY (Don't Repeat Yourself)",
            category=PrincipleCategory.ARCHITECTURE,
            severity=8,
            description="Eliminate code duplication through abstraction",
            violations=[
                "Duplicated code blocks (>5 lines)",
                "Similar methods without extraction",
                "Repeated conditional logic",
                "Copy-pasted code",
            ],
            detectable_patterns=["dup(", "clone("],
        ),
        ZenPrinciple(
            id="ruby-003",
            principle="Prefer blocks over lambdas/procs",
            category=PrincipleCategory.IDIOMS,
            severity=6,
            description="Use blocks for most iteration and callbacks",
            violations=[
                "Lambda where block would be clearer",
                "Proc for simple iterations",
                "Not using Ruby's block syntax",
            ],
            detectable_patterns=[
                "lambda { } for simple iterations",
                "Proc.new instead of block",
            ],
        ),
        ZenPrinciple(
            id="ruby-004",
            principle="Avoid monkey-patching core classes",
            category=PrincipleCategory.ARCHITECTURE,
            severity=9,
            description="Don't modify String, Array, or other core classes",
            violations=[
                "Reopening String class",
                "Reopening Array class",
                "Modifying Integer, Hash",
                "Adding methods to core classes",
            ],
            detectable_patterns=["class String", "class Array", "class Hash"],
        ),
        ZenPrinciple(
            id="ruby-005",
            principle="Use meaningful method names with ?/! convention",
            category=PrincipleCategory.READABILITY,
            severity=7,
            description="Methods ending in ? return boolean, ! indicate mutation",
            violations=[
                "Boolean methods without ?",
                "Mutating methods without !",
                "Inconsistent naming patterns",
            ],
            detectable_patterns=["def is", "def has"],
        ),
        ZenPrinciple(
            id="ruby-006",
            principle="Keep method chains readable",
            category=PrincipleCategory.READABILITY,
            severity=6,
            description="Limit method chaining to 3-4 calls",
            violations=[
                "Method chains > 4 calls",
                "Complex chaining without intermediate variables",
                "Unclear chaining logic",
            ],
            metrics={"max_method_chain_length": 4},
        ),
        ZenPrinciple(
            id="ruby-007",
            principle="Prefer symbols over strings for keys",
            category=PrincipleCategory.IDIOMS,
            severity=5,
            description="Use symbols for hash keys and identifiers",
            violations=[
                "String keys in hashes",
                "Strings for method names in send",
                "String identifiers",
            ],
            detectable_patterns=['=> "', "=> '"],
        ),
        ZenPrinciple(
            id="ruby-008",
            principle="Use guard clauses",
            category=PrincipleCategory.STRUCTURE,
            severity=6,
            description="Return early to avoid deep nesting",
            violations=[
                "Deep nested if-else",
                "Not using early returns",
                "Inverted logic creating nesting",
            ],
            detectable_patterns=["!return if"],
            recommended_alternative="return unless, return if",
        ),
        ZenPrinciple(
            id="ruby-009",
            principle="Avoid needless metaprogramming",
            category=PrincipleCategory.COMPLEXITY,
            severity=8,
            description="Use metaprogramming sparingly and only when necessary",
            violations=[
                "define_method without clear benefit",
                "method_missing abuse",
                "Overly clever class_eval",
                "Unnecessary send/public_send",
            ],
            detectable_patterns=[
                "define_method",
                "method_missing",
                "class_eval",
                "instance_eval",
                "send(",
            ],
        ),
        ZenPrinciple(
            id="ruby-010",
            principle="Use Ruby's expressive syntax",
            category=PrincipleCategory.IDIOMS,
            severity=6,
            description="Leverage Ruby's readable constructs",
            violations=[
                "for loops instead of .each",
                "unless with negation",
                "Not using &: syntax",
                "Ternary when if/else is clearer",
            ],
            detectable_patterns=["for item in collection", "unless !condition"],
        ),
        ZenPrinciple(
            id="ruby-011",
            principle="Prefer fail over raise for exceptions",
            category=PrincipleCategory.ERROR_HANDLING,
            severity=5,
            description="Use fail to indicate programmer errors",
            violations=[
                "Using raise for logic errors",
                "Not distinguishing error types",
            ],
            detectable_patterns=["raise "],
        ),
    ],
)
