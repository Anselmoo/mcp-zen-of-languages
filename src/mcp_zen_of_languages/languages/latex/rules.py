"""LaTeX zen principles as Pydantic models."""

from pydantic import HttpUrl

from mcp_zen_of_languages.rules.base_models import (
    LanguageZenPrinciples,
    PrincipleCategory,
    ZenPrinciple,
)

LATEX_ZEN = LanguageZenPrinciples(
    language="latex",
    name="LaTeX",
    philosophy="LaTeX document quality and semantic authoring",
    source_text="LaTeX Project",
    source_url=HttpUrl("https://www.latex-project.org/"),
    principles=[
        ZenPrinciple(
            id="latex-001",
            principle="Prefer \\newcommand over \\def",
            category=PrincipleCategory.CORRECTNESS,
            severity=7,
            description="Use checked macro definitions to avoid accidental redefinitions.",
            violations=["Raw \\def usage for user macros"],
        ),
        ZenPrinciple(
            id="latex-002",
            principle="Keep labels and references consistent",
            category=PrincipleCategory.CORRECTNESS,
            severity=8,
            description="Every label should be referenced and every reference should resolve.",
            violations=["Unused labels or unresolved \\ref/\\eqref targets"],
        ),
        ZenPrinciple(
            id="latex-003",
            principle="Require captions in figures and tables",
            category=PrincipleCategory.DOCUMENTATION,
            severity=6,
            description="Figure and table environments should include captions for context.",
            violations=["Figure/table without \\caption"],
        ),
        ZenPrinciple(
            id="latex-004",
            principle="Maintain bibliography hygiene",
            category=PrincipleCategory.ORGANIZATION,
            severity=6,
            description="Prefer citation keys with bibliography files and avoid uncited entries.",
            violations=["Manual \\bibitem blocks or uncited bibliography items"],
        ),
        ZenPrinciple(
            id="latex-005",
            principle="Avoid hardcoded absolute lengths",
            category=PrincipleCategory.CONSISTENCY,
            severity=5,
            description="Prefer relative lengths such as \\textwidth and \\linewidth.",
            violations=["Absolute units like pt/cm/mm/in in layout-sensitive commands"],
        ),
        ZenPrinciple(
            id="latex-006",
            principle="Prefer semantic emphasis commands",
            category=PrincipleCategory.CLARITY,
            severity=4,
            description="Use semantic markup over direct visual styling commands.",
            violations=["\\textit or \\textbf used as semantic emphasis"],
        ),
        ZenPrinciple(
            id="latex-007",
            principle="Prevent circular \\input and \\include chains",
            category=PrincipleCategory.ARCHITECTURE,
            severity=8,
            description="Included files must not create recursive include loops.",
            violations=["Circular \\input/\\include dependency"],
        ),
        ZenPrinciple(
            id="latex-008",
            principle="Declare UTF-8 encoding intent",
            category=PrincipleCategory.CORRECTNESS,
            severity=5,
            description="Declare UTF-8 input encoding unless using LuaTeX/XeTeX native flow.",
            violations=["Missing UTF-8 encoding declaration"],
        ),
        ZenPrinciple(
            id="latex-009",
            principle="Remove unused packages",
            category=PrincipleCategory.ORGANIZATION,
            severity=5,
            description="Declared packages should have commands used in the document.",
            violations=["\\usepackage declarations with no usage"],
        ),
    ],
)
