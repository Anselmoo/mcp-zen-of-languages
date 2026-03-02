"""Markdown/MDX zen principles as Pydantic models."""

from pydantic import HttpUrl

from mcp_zen_of_languages.rules.base_models import LanguageZenPrinciples
from mcp_zen_of_languages.rules.base_models import PrincipleCategory
from mcp_zen_of_languages.rules.base_models import ZenPrinciple


MARKDOWN_ZEN = LanguageZenPrinciples(
    language="markdown",
    name="Markdown / MDX",
    philosophy="Documentation structure, accessibility, and MDX component hygiene",
    source_text="CommonMark + MDX authoring best practices",
    source_url=HttpUrl("https://commonmark.org/"),
    principles=[
        ZenPrinciple(
            id="md-001",
            principle="Preserve heading hierarchy",
            category=PrincipleCategory.STRUCTURE,
            severity=6,
            description="Documents should begin with an H1 and avoid heading level skips.",
            violations=[
                "Heading level jump greater than one level",
                "Document missing top-level H1 heading",
            ],
        ),
        ZenPrinciple(
            id="md-002",
            principle="Images require meaningful alt text",
            category=PrincipleCategory.USABILITY,
            severity=8,
            description="Every Markdown image should include non-empty alternative text.",
            violations=["Image markdown with empty alt text"],
            detectable_patterns=[r"!\[\s*\]\("],
        ),
        ZenPrinciple(
            id="md-003",
            principle="Avoid bare URLs in prose",
            category=PrincipleCategory.CLARITY,
            severity=5,
            description="Raw URLs should be wrapped as Markdown links or angle-bracket autolinks.",
            violations=["Bare URL in prose text"],
            detectable_patterns=[r"https?://"],
        ),
        ZenPrinciple(
            id="md-004",
            principle="Fence code blocks with explicit language tags",
            category=PrincipleCategory.DOCUMENTATION,
            severity=4,
            description="Fenced code blocks should declare a language for syntax highlighting.",
            violations=["Code fence missing language identifier"],
            detectable_patterns=[r"\`\`\`"],
        ),
        ZenPrinciple(
            id="md-005",
            principle="Keep relative links and metadata healthy",
            category=PrincipleCategory.DOCUMENTATION,
            severity=6,
            description="Validate front-matter keys when present and flag dead relative links.",
            violations=[
                "Front-matter is missing required keys",
                "Relative Markdown link target does not exist",
            ],
            metrics={"required_frontmatter_keys": ["title", "description"]},
        ),
        ZenPrinciple(
            id="md-006",
            principle="Use named default exports in MDX",
            category=PrincipleCategory.CORRECTNESS,
            severity=6,
            description="Avoid anonymous default exports in MDX modules.",
            violations=["Unnamed default export in MDX"],
        ),
        ZenPrinciple(
            id="md-007",
            principle="Keep MDX imports hygienic",
            category=PrincipleCategory.ORGANIZATION,
            severity=5,
            description="Imported MDX components should be used in JSX or module code.",
            violations=["Imported MDX component is never used"],
        ),
    ],
)
