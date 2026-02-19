"""Template for adding new language zen principles.

Copy this file and rename it to {language}_zen.py
Then fill in the principles for your target language.
"""

from pydantic import HttpUrl

from ..base_models import LanguageZenPrinciples, PrincipleCategory, ZenPrinciple

# Replace TEMPLATE with your language name (e.g., TYPESCRIPT, RUBY, GO)
TEMPLATE_ZEN = LanguageZenPrinciples(
    language="template",  # lowercase identifier
    name="Template Language",  # Human-readable name
    philosophy="Core philosophy or guiding principle",
    source_text="Style Guide",
    source_url=HttpUrl("https://example.com/style-guide"),
    principles=[
        # Example principle - copy and modify this for each principle
        ZenPrinciple(
            id="template-001",  # Format: {language}-{number}
            principle="Short statement of the principle",
            category=PrincipleCategory.ERROR_HANDLING,  # Choose appropriate category
            severity=7,  # 1-10 scale
            description="Detailed explanation of what this principle means",
            violations=[
                "Common violation pattern 1",
                "Common violation pattern 2",
                "Common violation pattern 3",
            ],
            detectable_patterns=["Specific code pattern to detect", "Another pattern"],
            metrics={"max_something": 10, "threshold_value": 50},
            recommended_alternative="Suggested fix or better approach",
        ),
        # Add more principles here...
        ZenPrinciple(
            id="template-002",
            principle="Another principle",
            category=PrincipleCategory.TYPE_SAFETY,
            severity=9,
            description="Another principle description",
            violations=["Violation example"],
        ),
    ],
)

# Quick reference for PrincipleCategory options:
"""
PrincipleCategory.READABILITY
PrincipleCategory.CLARITY
PrincipleCategory.COMPLEXITY
PrincipleCategory.ARCHITECTURE
PrincipleCategory.STRUCTURE
PrincipleCategory.CONSISTENCY
PrincipleCategory.ERROR_HANDLING
PrincipleCategory.CORRECTNESS
PrincipleCategory.IDIOMS
PrincipleCategory.ORGANIZATION
PrincipleCategory.ASYNC
PrincipleCategory.IMMUTABILITY
PrincipleCategory.TYPE_SAFETY
PrincipleCategory.DESIGN
PrincipleCategory.FUNCTIONAL
PrincipleCategory.CONFIGURATION
PrincipleCategory.CONCURRENCY
PrincipleCategory.INITIALIZATION
PrincipleCategory.PERFORMANCE
PrincipleCategory.DEBUGGING
PrincipleCategory.SAFETY
PrincipleCategory.OWNERSHIP
PrincipleCategory.RESOURCE_MANAGEMENT
PrincipleCategory.MEMORY_MANAGEMENT
PrincipleCategory.SCOPE
PrincipleCategory.SECURITY
PrincipleCategory.ROBUSTNESS
PrincipleCategory.USABILITY
PrincipleCategory.NAMING
PrincipleCategory.DOCUMENTATION
"""

# Severity guidelines:
"""
1-3: Informational - Minor style deviation
4-6: Warning - Moderate violation
7-8: Error - Significant architectural issue
9-10: Critical - Severe zen violation or safety concern
"""
