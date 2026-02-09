#!/usr/bin/env python3
"""Content pipeline: markdown/HTML → styled PDF pages.

Usage:
    python render.py --brand <brand-kit-path> --input <content.html> --output <content-pages.pdf> [--format A4|Letter] [--debug]

Renders HTML content into paginated PDF pages using brand kit tokens.
Uses xhtml2pdf for flowing text and reportlab for precise elements.
"""
import argparse
import json
import os
import sys
from pathlib import Path


def load_brand(brand_path: str) -> dict:
    """Load brand manifest and resolve asset paths."""
    brand_dir = Path(brand_path)
    manifest_path = brand_dir / "assets" / "manifest.json"
    if not manifest_path.exists():
        print(f"Error: Brand manifest not found at {manifest_path}", file=sys.stderr)
        sys.exit(1)
    with open(manifest_path) as f:
        manifest = json.load(f)
    manifest["_base_path"] = str(brand_dir / "assets")
    return manifest


def load_fallback() -> dict:
    """Load fallback defaults when no brand kit is specified."""
    fallback_dir = Path(__file__).parent.parent / "assets" / "fallback"
    return {
        "brand": {"name": "Default", "slug": "default", "version": "1.0.0"},
        "fonts": {
            "body": {"regular": str(fallback_dir / "body.ttf"), "bold": str(fallback_dir / "body-bold.ttf"), "italic": str(fallback_dir / "body-italic.ttf")},
            "mono": {"regular": str(fallback_dir / "mono.ttf")},
        },
        "defaults": {"page_format": "A4"},
        "_base_path": str(fallback_dir),
        "_fallback": True,
    }


def register_fonts(manifest: dict):
    """Register all brand fonts with reportlab."""
    from reportlab.lib.fonts import addMapping
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    base = manifest["_base_path"]
    fonts = manifest.get("fonts", {})
    for role, variants in fonts.items():
        if isinstance(variants, dict):
            for variant, rel_path in variants.items():
                font_path = os.path.join(base, rel_path) if not os.path.isabs(rel_path) else rel_path
                if os.path.exists(font_path) and os.path.getsize(font_path) > 0:
                    font_name = f"Brand-{role}-{variant}"
                    try:
                        pdfmetrics.registerFont(TTFont(font_name, font_path))
                    except Exception as e:
                        print(f"Warning: Could not register font {font_name}: {e}", file=sys.stderr)


def build_stylesheet(manifest: dict, css_path: str = None) -> str:
    """Build CSS stylesheet from brand tokens and base.css template."""
    base_css_path = css_path or str(Path(__file__).parent.parent / "assets" / "css" / "base.css")
    css = ""
    if os.path.exists(base_css_path):
        with open(base_css_path) as f:
            css = f.read()
    return css


def render_html_to_pdf(html: str, output_path: str, manifest: dict, page_format: str = "A4", debug: bool = False):
    """Render HTML content to PDF pages."""
    from xhtml2pdf import pisa

    css = build_stylesheet(manifest)
    full_html = f"""<!DOCTYPE html>
<html>
<head><style>{css}</style></head>
<body>{html}</body>
</html>"""

    with open(output_path, "wb") as out_file:
        status = pisa.CreatePDF(full_html, dest=out_file)

    if status.err:
        print(f"Error: xhtml2pdf reported {status.err} errors", file=sys.stderr)
        sys.exit(1)

    print(f"Rendered content pages to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Render HTML content to styled PDF pages")
    parser.add_argument("--brand", required=False, help="Path to brand kit skill directory")
    parser.add_argument("--input", required=True, help="Path to HTML content file")
    parser.add_argument("--output", required=True, help="Output PDF path")
    parser.add_argument("--format", default="A4", choices=["A4", "Letter"], help="Page format")
    parser.add_argument("--debug", action="store_true", help="Show grid lines and zone boundaries")
    args = parser.parse_args()

    if args.brand:
        manifest = load_brand(args.brand)
    else:
        manifest = load_fallback()

    register_fonts(manifest)

    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    with open(args.input) as f:
        html = f.read()

    render_html_to_pdf(html, args.output, manifest, page_format=args.format, debug=args.debug)


if __name__ == "__main__":
    main()
