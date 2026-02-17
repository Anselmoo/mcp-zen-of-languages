"""Pre-commit/CI gate: run runtime WCAG AA contrast checks for built docs pages."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, sync_playwright

CONFIG_PATH = Path("scripts/docs_contrast_config.json")
DEFAULT_SITE_DIR = Path("site")
DEFAULT_REPORT_PATH = Path("tmp/contrast-report.json")


@dataclass(slots=True)
class ContrastCheck:
    """Represents one selector-based contrast rule."""

    name: str
    selector: str
    min_ratio: float


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=CONFIG_PATH,
        help="Path to contrast audit config JSON.",
    )
    parser.add_argument(
        "--site-dir",
        type=Path,
        default=DEFAULT_SITE_DIR,
        help="Built MkDocs site directory.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="Path to JSON report output.",
    )
    parser.add_argument(
        "--screenshot-dir",
        type=Path,
        default=None,
        help="Optional baseline screenshot output directory.",
    )
    parser.add_argument(
        "--mode",
        choices=["check", "baseline"],
        default="check",
        help="check: enforce and fail on violations; baseline: produce artifacts only.",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Build docs with mkdocs before running checks.",
    )
    parser.add_argument(
        "--limit-pages",
        type=int,
        default=0,
        help="Optional page cap for local debugging (0 = all pages).",
    )
    return parser.parse_args()


def load_config(path: Path) -> tuple[list[str], list[ContrastCheck], list[str], int]:
    """Load configuration from JSON file."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    schemes = [str(scheme) for scheme in payload["schemes"]]
    checks = [
        ContrastCheck(
            name=str(item["name"]),
            selector=str(item["selector"]),
            min_ratio=float(item["min_ratio"]),
        )
        for item in payload["checks"]
    ]
    ignore_selectors = [
        str(selector) for selector in payload.get("ignore_selectors", [])
    ]
    max_failures = int(payload.get("max_failures_per_check_per_page", 25))
    return schemes, checks, ignore_selectors, max_failures


def build_docs() -> None:
    """Build docs site with deterministic, local-safe environment flags."""
    env = os.environ.copy()
    env.setdefault("MKDOCS_SOCIAL_ENABLED", "false")
    env.setdefault("MKDOCS_GIT_REVISION_ENABLED", "false")
    subprocess.run(
        ["uv", "run", "mkdocs", "build", "--strict"],
        check=True,
        env=env,
    )


def discover_pages(site_dir: Path) -> list[str]:
    """Return URL paths for all built HTML pages."""
    pages: list[str] = []
    for html_file in sorted(site_dir.rglob("*.html")):
        rel = html_file.relative_to(site_dir).as_posix()
        if rel.endswith("404.html"):
            continue
        if rel == "index.html":
            pages.append("/")
            continue
        if rel.endswith("/index.html"):
            pages.append("/" + rel.removesuffix("index.html"))
            continue
        pages.append("/" + rel)
    return pages


class QuietHandler(SimpleHTTPRequestHandler):
    """HTTP handler with suppressed access logs."""

    def log_message(self, format: str, *args: Any) -> None:
        return


@contextmanager
def serve_site(site_dir: Path) -> Iterator[tuple[str, ThreadingHTTPServer]]:
    """Serve the built site from an ephemeral local port."""
    handler = partial(QuietHandler, directory=str(site_dir))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host = str(server.server_address[0])
    port = int(server.server_address[1])
    try:
        yield f"http://{host}:{port}", server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def apply_scheme(page: Page, scheme: str) -> None:
    """Force a specific material color scheme on current page."""
    page.evaluate(
        """
        (scheme) => {
          const root = document.documentElement;
          const body = document.body;
          root.setAttribute("data-md-color-scheme", scheme);
          if (body) {
            body.setAttribute("data-md-color-scheme", scheme);
          }
          const palette = { color: { media: "", scheme }, primary: "custom", accent: "custom" };
          localStorage.setItem("__palette", JSON.stringify(palette));
        }
        """,
        scheme,
    )
    page.wait_for_timeout(250)


JS_AUDIT_SNIPPET = """
({ checks, ignoreSelectors, maxFailuresPerCheck }) => {
  const parseColor = (value) => {
    if (!value) return { r: 0, g: 0, b: 0, a: 0 };
    const cleaned = value.trim().toLowerCase();
    if (cleaned === "transparent") return { r: 0, g: 0, b: 0, a: 0 };
    const match = cleaned.match(/rgba?\\(([^)]+)\\)/);
    if (!match) return { r: 0, g: 0, b: 0, a: 0 };
    const parts = match[1].split(",").map((part) => parseFloat(part.trim()));
    if (parts.length === 3) {
      return { r: parts[0], g: parts[1], b: parts[2], a: 1 };
    }
    return { r: parts[0], g: parts[1], b: parts[2], a: Number.isFinite(parts[3]) ? parts[3] : 1 };
  };

  const blend = (fg, bg) => {
    const alpha = fg.a + bg.a * (1 - fg.a);
    if (alpha <= 0) return { r: 0, g: 0, b: 0, a: 0 };
    return {
      r: ((fg.r * fg.a) + (bg.r * bg.a * (1 - fg.a))) / alpha,
      g: ((fg.g * fg.a) + (bg.g * bg.a * (1 - fg.a))) / alpha,
      b: ((fg.b * fg.a) + (bg.b * bg.a * (1 - fg.a))) / alpha,
      a: alpha
    };
  };

  const linear = (channel) => {
    const value = channel / 255;
    return value <= 0.03928 ? value / 12.92 : Math.pow((value + 0.055) / 1.055, 2.4);
  };

  const luminance = (color) => (
    0.2126 * linear(color.r) +
    0.7152 * linear(color.g) +
    0.0722 * linear(color.b)
  );

  const contrast = (a, b) => {
    const l1 = luminance(a);
    const l2 = luminance(b);
    const bright = Math.max(l1, l2);
    const dark = Math.min(l1, l2);
    return (bright + 0.05) / (dark + 0.05);
  };

  const isVisible = (el) => {
    if (!(el instanceof Element)) return false;
    const style = getComputedStyle(el);
    if (style.display === "none" || style.visibility === "hidden" || Number.parseFloat(style.opacity) <= 0) {
      return false;
    }
    const rect = el.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  };

  const shouldIgnore = (el) => {
    for (const selector of ignoreSelectors) {
      if (el.matches(selector) || el.closest(selector)) return true;
    }
    return false;
  };

  const baseBackground = () => {
    const bodyColor = parseColor(getComputedStyle(document.body).backgroundColor);
    if (bodyColor.a > 0) return bodyColor;
    const rootColor = parseColor(getComputedStyle(document.documentElement).backgroundColor);
    if (rootColor.a > 0) return rootColor;
    return { r: 255, g: 255, b: 255, a: 1 };
  };

  const effectiveBackground = (el) => {
    let bg = baseBackground();
    const chain = [];
    let node = el;
    while (node && node instanceof Element) {
      chain.push(node);
      node = node.parentElement;
    }
    chain.reverse();
    for (const current of chain) {
      const layer = parseColor(getComputedStyle(current).backgroundColor);
      if (layer.a > 0) {
        bg = blend(layer, bg);
      }
    }
    return bg;
  };

  const toHex = (color) => {
    const toByte = (value) => {
      const clamped = Math.max(0, Math.min(255, Math.round(value)));
      return clamped.toString(16).padStart(2, "0");
    };
    return `#${toByte(color.r)}${toByte(color.g)}${toByte(color.b)}`;
  };

  const summarize = [];

  for (const check of checks) {
    let elements = [];
    try {
      elements = Array.from(document.querySelectorAll(check.selector));
    } catch (_error) {
      summarize.push({
        check: check.name,
        selector: check.selector,
        measured: 0,
        minRatioSeen: null,
        failures: []
      });
      continue;
    }
    let measured = 0;
    let minRatioSeen = Number.POSITIVE_INFINITY;
    const failures = [];

    for (const el of elements) {
      if (!(el instanceof Element)) continue;
      if (!isVisible(el) || shouldIgnore(el)) continue;

      const style = getComputedStyle(el);
      const fg = parseColor(style.color);
      if (fg.a <= 0) continue;

      const bg = effectiveBackground(el);
      const ratio = contrast(fg, bg);
      const fontSize = Number.parseFloat(style.fontSize) || 16;
      const fontWeight = Number.parseInt(style.fontWeight, 10) || 400;
      const isLarge = fontSize >= 24 || (fontSize >= 18.66 && fontWeight >= 700);
      const threshold = isLarge ? Math.min(check.min_ratio, 3) : check.min_ratio;

      measured += 1;
      if (ratio < minRatioSeen) minRatioSeen = ratio;

      if (ratio < threshold && failures.length < maxFailuresPerCheck) {
        const text = (el.textContent || "").trim().replace(/\\s+/g, " ").slice(0, 120);
        failures.push({
          check: check.name,
          selector: check.selector,
          ratio,
          threshold,
          text,
          fg: toHex(fg),
          bg: toHex(bg),
          fontSize: style.fontSize,
          fontWeight: style.fontWeight
        });
      }
    }

    summarize.push({
      check: check.name,
      selector: check.selector,
      measured,
      minRatioSeen: Number.isFinite(minRatioSeen) ? minRatioSeen : null,
      failures
    });
  }

  return summarize;
}
"""


def run_audit(
    base_url: str,
    pages: list[str],
    schemes: list[str],
    checks: list[ContrastCheck],
    ignore_selectors: list[str],
    max_failures: int,
    screenshot_dir: Path | None,
) -> dict[str, Any]:
    """Execute contrast checks and return audit report."""
    results: list[dict[str, Any]] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(viewport={"width": 1400, "height": 1000})
        page = context.new_page()

        for path in pages:
            url = f"{base_url}{path}"
            page.goto(url, wait_until="networkidle")
            for scheme in schemes:
                apply_scheme(page, scheme)
                checks_payload = [
                    {
                        "name": item.name,
                        "selector": item.selector,
                        "min_ratio": item.min_ratio,
                    }
                    for item in checks
                ]
                summaries = page.evaluate(
                    JS_AUDIT_SNIPPET,
                    {
                        "checks": checks_payload,
                        "ignoreSelectors": ignore_selectors,
                        "maxFailuresPerCheck": max_failures,
                    },
                )
                page_result = {
                    "page": path,
                    "scheme": scheme,
                    "checks": summaries,
                }
                results.append(page_result)

                if screenshot_dir is not None:
                    output_file = (
                        screenshot_dir
                        / scheme
                        / (
                            "index.png"
                            if path == "/"
                            else path.strip("/").replace("/", "__") + ".png"
                        )
                    )
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(output_file), full_page=True)

        context.close()
        browser.close()

    matrix: dict[str, dict[str, Any]] = {}
    failures: list[dict[str, Any]] = []
    for entry in results:
        scheme = entry["scheme"]
        for check in entry["checks"]:
            key = f"{scheme}::{check['check']}"
            summary = matrix.setdefault(
                key,
                {
                    "scheme": scheme,
                    "check": check["check"],
                    "selector": check["selector"],
                    "pages_measured": 0,
                    "elements_measured": 0,
                    "failing_elements": 0,
                    "min_ratio_seen": None,
                },
            )
            summary["pages_measured"] += 1
            summary["elements_measured"] += int(check["measured"])
            summary["failing_elements"] += len(check["failures"])
            ratio = check["minRatioSeen"]
            if ratio is not None:
                if summary["min_ratio_seen"] is None:
                    summary["min_ratio_seen"] = ratio
                else:
                    summary["min_ratio_seen"] = min(summary["min_ratio_seen"], ratio)

            for failure in check["failures"]:
                failures.append(
                    {
                        "page": entry["page"],
                        "scheme": scheme,
                        **failure,
                    }
                )

    return {
        "summary": {
            "pages": len(pages),
            "schemes": schemes,
            "checks": [item.name for item in checks],
            "failures": len(failures),
        },
        "matrix": sorted(
            matrix.values(), key=lambda item: (item["scheme"], item["check"])
        ),
        "failures": failures,
    }


def print_summary(report: dict[str, Any]) -> None:
    """Render a short terminal summary."""
    summary = report["summary"]
    print("Docs contrast audit summary")
    print(f"- Pages: {summary['pages']}")
    print(f"- Schemes: {', '.join(summary['schemes'])}")
    print(f"- Components checked: {len(summary['checks'])}")
    print(f"- Failures: {summary['failures']}")

    if report["failures"]:
        print("\nTop failures:")
        for failure in report["failures"][:10]:
            print(
                "  - "
                f"[{failure['scheme']}] {failure['page']} :: {failure['check']} "
                f"ratio={failure['ratio']:.2f} < {failure['threshold']:.2f} "
                f"fg={failure['fg']} bg={failure['bg']} text='{failure['text']}'"
            )


def main() -> int:
    """Run docs contrast checks."""
    args = parse_args()
    schemes, checks, ignore_selectors, max_failures = load_config(args.config)

    if args.build:
        build_docs()

    if not args.site_dir.exists():
        print(f"Site directory not found: {args.site_dir}", file=sys.stderr)
        return 2

    pages = discover_pages(args.site_dir)
    if args.limit_pages > 0:
        pages = pages[: args.limit_pages]

    with serve_site(args.site_dir) as (base_url, _server):
        report = run_audit(
            base_url=base_url,
            pages=pages,
            schemes=schemes,
            checks=checks,
            ignore_selectors=ignore_selectors,
            max_failures=max_failures,
            screenshot_dir=args.screenshot_dir,
        )

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print_summary(report)
    print(f"\nReport written to {args.report}")

    if args.mode == "check" and report["summary"]["failures"] > 0:
        print("\n❌ Contrast checks failed (WCAG AA).")
        return 1

    print("\n✅ Contrast checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
