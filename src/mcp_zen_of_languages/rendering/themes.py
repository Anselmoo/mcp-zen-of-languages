"""Theme palette, box constants, and severity-aware glyph helpers.

Defines ``ZEN_THEME`` — the Rich ``Theme`` instance shared by both console
singletons — which maps semantic tokens (``severity.critical``,
``metric``, ``banner``, …) to Rich style strings.  Five box-style
constants (``BOX_BANNER``, ``BOX_SUMMARY``, ``BOX_CONTENT``, ``BOX_ACTION``,
``BOX_CODE``) standardise panel borders across all CLI surfaces.

Glyph helpers (``severity_badge``, ``pass_fail_glyph``, ``file_glyph``,
``score_glyph``) return emoji on capable terminals and fall back to
ASCII on legacy Windows consoles, detected once via ``_use_emoji``.

Brand palette (Caligo design system — docs/stylesheets/tokens/palette.css):
  BRAND_PRIMARY  #989cff  Soft purple — primary UI colour (caligo-accent)
  BRAND_ACCENT   #c8315a  Cherry red — vibrant highlights, required, scores
  BRAND_COOL     #63c8ff  Cool cyan — success, low-severity, switches
  BRAND_MUTED    #9b95ad  Muted purple-gray — dim/subtle elements
  BORDER_STYLE   #767bd8  Subdued purple — panel borders (caligo-accent-muted)
"""

from __future__ import annotations

from functools import lru_cache

from rich import box
from rich.console import Console
from rich.theme import Theme


# ── Brand color palette (Caligo design system) ──────────────────────
BRAND_PRIMARY = "#989cff"  # caligo-accent: soft purple — primary UI colour
BRAND_ACCENT = "#c8315a"  # caligo-cherry: vibrant red — highlights, scores
BRAND_COOL = "#63c8ff"  # caligo-harmony-cool: bright cyan — success, switches
BRAND_MUTED = "#9b95ad"  # caligo-fg-muted: muted purple-gray — dim elements


# Panel borders use subdued purple — coherent with primary but less prominent
BORDER_STYLE = "#767bd8"  # caligo-accent-muted

# Severity tier thresholds (1-10 scale)
SEVERITY_CRITICAL = 9
SEVERITY_HIGH = 7
SEVERITY_MEDIUM = 4

ZEN_THEME = Theme(
    {
        "severity.critical": "bold red",
        "severity.high": f"bold {BRAND_ACCENT}",
        "severity.medium": BRAND_PRIMARY,
        "severity.low": BRAND_COOL,
        "path": f"bold {BRAND_PRIMARY}",
        "metric": BRAND_PRIMARY,
        "score": f"bold {BRAND_ACCENT}",
        "banner": f"bold {BRAND_PRIMARY}",
        "muted": f"dim {BRAND_MUTED}",
    },
)

BOX_BANNER = box.DOUBLE
BOX_SUMMARY = box.HEAVY
BOX_CONTENT = box.ROUNDED
BOX_ACTION = box.SIMPLE
BOX_CODE = box.SQUARE


def severity_style(severity: int) -> str:
    """Map a numeric severity score (1-10) to a Rich style token.

    The mapping follows four tiers that correspond to the
    ``ZEN_THEME`` severity entries:

    * **≥ 9** → ``severity.critical`` (bold red)
    * **≥ 7** → ``severity.high`` (bold orange)
    * **≥ 4** → ``severity.medium`` (steel blue)
    * **< 4** → ``severity.low`` (earthy green)

    Args:
        severity (int): Integer severity score assigned to a violation.

    Returns:
        str: Theme token name usable with Rich ``style=`` parameters.
    """
    if severity >= SEVERITY_CRITICAL:
        return "severity.critical"
    if severity >= SEVERITY_HIGH:
        return "severity.high"
    return "severity.medium" if severity >= SEVERITY_MEDIUM else "severity.low"


def severity_badge(severity: int) -> str:
    """Produce a coloured Rich-markup badge for a severity tier.

    Returns an inline Rich markup string combining a glyph and a
    short label (``CRIT``, ``HIGH``, ``MED``, ``LOW``) wrapped in the
    matching ``severity.*`` style tag.  Emoji glyphs (🔴, 🟠, 🔵, ⚪)
    are used on capable terminals; ASCII fallbacks (●, ▲, ◆, ○) on
    legacy Windows consoles.

    Args:
        severity (int): Integer severity score (1-10) determining the badge tier.

    Returns:
        str: Rich markup string that renders as a coloured badge when printed.
    """
    if severity >= SEVERITY_CRITICAL:
        style, label = "severity.critical", "CRIT"
    elif severity >= SEVERITY_HIGH:
        style, label = "severity.high", "HIGH"
    elif severity >= SEVERITY_MEDIUM:
        style, label = "severity.medium", "MED"
    else:
        style, label = "severity.low", "LOW"
    glyphs = (
        {
            "severity.critical": "🔴",
            "severity.high": "🟠",
            "severity.medium": "🔵",
            "severity.low": "⚪",
        }
        if _use_emoji()
        else {
            "severity.critical": "●",
            "severity.high": "▲",
            "severity.medium": "◆",
            "severity.low": "○",
        }
    )
    return f"[{style}]{glyphs[style]} {label}[/]"


def pass_fail_glyph(*, passed: bool) -> str:
    """Return a pass (✅ / ``[OK]``) or fail (❌ / ``[FAIL]``) indicator.

    Used in summary lines and ``print_error`` to give instant visual
    feedback.  Emoji variants are chosen on capable terminals; ASCII
    text fallbacks are used on legacy Windows consoles.

    Args:
        passed (bool): True for the success glyph, False for the failure glyph.

    Returns:
        str: Single-glyph string suitable for inline concatenation.
    """
    if _use_emoji():
        return "✅" if passed else "❌"
    return "[OK]" if passed else "[FAIL]"


def file_glyph() -> str:
    """Return a file icon glyph (📄) or ASCII dash fallback.

    Used in report headers to visually tag the target file path.

    Returns:
        str: Single-character glyph suitable for inline concatenation.
    """
    return "📄" if _use_emoji() else "-"


def score_glyph() -> str:
    """Return a star glyph (⭐) or ASCII asterisk fallback.

    Used next to numeric quality scores in summary tables to draw
    attention to the overall result.

    Returns:
        str: Single-character glyph suitable for inline concatenation.
    """
    return "⭐" if _use_emoji() else "*"


@lru_cache(maxsize=1)
def _use_emoji() -> bool:
    """Detect whether the terminal can render emoji glyphs.

    Creates a throwaway ``Console`` and checks its ``legacy_windows``
    flag.  The result is cached for the process lifetime so the
    detection cost is paid only once.

    Returns:
        bool: True on modern terminals; False on legacy Windows consoles.
    """
    return not Console().options.legacy_windows
