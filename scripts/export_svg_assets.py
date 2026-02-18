#!/usr/bin/env python3
"""Export project SVG assets to PNG files with a consistent renderer flow."""

from __future__ import annotations

import argparse
import re
from contextlib import suppress
from pathlib import Path

DEFAULT_ASSETS: tuple[tuple[Path, Path, int | None, int | None], ...] = (
    (Path("docs/assets/logo.svg"), Path("docs/assets/logo.png"), None, None),
    (Path("docs/assets/hero-zen.svg"), Path("docs/assets/hero-zen.png"), None, None),
    (
        Path("docs/assets/social-card-bg.svg"),
        Path("docs/assets/social-card-bg.png"),
        1200,
        630,
    ),
    (
        Path("docs/assets/social-card-github.svg"),
        Path("docs/assets/social-card-github.png"),
        1280,
        640,
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export default project SVG assets to PNG files.",
    )
    parser.add_argument(
        "--asset",
        action="append",
        default=[],
        help=(
            "Optional custom mapping '<input_svg>:<output_png>' (can be repeated). "
            "When provided, custom mappings are added after default assets."
        ),
    )
    return parser.parse_args()


def _parse_custom_assets(
    raw_assets: list[str],
) -> list[tuple[Path, Path, int | None, int | None]]:
    parsed_assets: list[tuple[Path, Path, int | None, int | None]] = []
    for raw_asset in raw_assets:
        input_part, separator, output_part = raw_asset.partition(":")
        if separator == "" or not input_part.strip() or not output_part.strip():
            raise SystemExit(
                "Invalid --asset value. Expected '<input_svg>:<output_png>' format."
            )

        parsed_assets.append(
            (Path(input_part.strip()), Path(output_part.strip()), None, None)
        )

    return parsed_assets


def _extract_dimensions(svg_text: str) -> tuple[int, int]:
    width_match = re.search(r'\bwidth="([0-9]+(?:\.[0-9]+)?)', svg_text)
    height_match = re.search(r'\bheight="([0-9]+(?:\.[0-9]+)?)', svg_text)
    if width_match and height_match:
        return int(float(width_match[1])), int(float(height_match[1]))

    if viewbox_match := re.search(
        r'\bviewBox="[0-9.\-]+\s+[0-9.\-]+\s+([0-9.\-]+)\s+([0-9.\-]+)"',
        svg_text,
    ):
        return int(float(viewbox_match[1])), int(float(viewbox_match[2]))

    return 1200, 630


def _export_with_playwright(
    input_path: Path,
    output_path: Path,
    width: int | None,
    height: int | None,
) -> None:
    from playwright.sync_api import sync_playwright

    svg_text = input_path.read_text(encoding="utf-8")
    resolved_width, resolved_height = (
        (width, height) if width and height else _extract_dimensions(svg_text)
    )
    # Inject explicit dimensions so SVGs with only a viewBox
    # fill the viewport instead of collapsing to 0x0.
    svg_sized = re.sub(
        r"<svg\b",
        f'<svg width="{resolved_width}" height="{resolved_height}"',
        svg_text,
        count=1,
    )
    html = f"""<!doctype html>
<html>
  <body style="margin:0;padding:0;overflow:hidden;">
    {svg_sized}
  </body>
</html>"""

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(
            viewport={"width": resolved_width, "height": resolved_height}
        )
        page.set_content(html)
        page.screenshot(path=str(output_path), omit_background=True)
        browser.close()


def _export_with_cairosvg(
    input_path: Path,
    output_path: Path,
    width: int | None,
    height: int | None,
) -> None:
    from cairosvg import svg2png

    kwargs: dict[str, object] = {
        "url": str(input_path),
        "write_to": str(output_path),
    }
    if width is not None and height is not None:
        kwargs["output_width"] = width
        kwargs["output_height"] = height
    svg2png(**kwargs)


def _export_one(
    input_path: Path,
    output_path: Path,
    width: int | None,
    height: int | None,
) -> None:
    if not input_path.exists():
        raise SystemExit(f"Input SVG not found: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with suppress(Exception):
        _export_with_playwright(
            input_path=input_path,
            output_path=output_path,
            width=width,
            height=height,
        )
        return

    try:
        _export_with_cairosvg(
            input_path=input_path,
            output_path=output_path,
            width=width,
            height=height,
        )
    except (ImportError, OSError) as exc:
        raise SystemExit(
            "Unable to export PNG. Install a Playwright browser via "
            "`uv run python -m playwright install chromium` or install cairo for CairoSVG."
        ) from exc


def main() -> int:
    args = parse_args()
    assets = [*DEFAULT_ASSETS, *_parse_custom_assets(args.asset)]

    for input_path, output_path, width, height in assets:
        _export_one(
            input_path=input_path,
            output_path=output_path,
            width=width,
            height=height,
        )
        if width is not None and height is not None:
            print(f"Exported {input_path} -> {output_path} ({width}x{height})")
        else:
            print(f"Exported {input_path} -> {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
