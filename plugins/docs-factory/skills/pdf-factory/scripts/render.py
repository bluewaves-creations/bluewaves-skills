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

# Default tokens used by fallback mode and as a safety net
_DEFAULT_TOKENS = {
    "colors": {
        "text-heading": "#1A1A1A",
        "text-body": "#1A1A1A",
        "text-muted": "#7A7A7A",
        "text-inverse": "#FFFFFF",
        "background-page": "#FFFFFF",
        "background-alt": "#F0F0F0",
        "border-default": "#B0B0B0",
        "border-strong": "#4A4A4A",
        "link": "#2E7D8C",
        "highlight": "#E8A838",
    },
    "type_scale": {
        "display-lg": {"size_pt": 72, "weight": "bold",  "font": "heading", "line_height": 1.0},
        "display":  {"size_pt": 48, "weight": "bold",    "font": "heading", "line_height": 1.1},
        "h1":       {"size_pt": 32, "weight": "bold",    "font": "heading", "line_height": 1.15},
        "h2":       {"size_pt": 24, "weight": "bold",    "font": "heading", "line_height": 1.2},
        "h3":       {"size_pt": 18, "weight": "bold",    "font": "heading", "line_height": 1.25},
        "h4":       {"size_pt": 14, "weight": "bold",    "font": "heading", "line_height": 1.3},
        "body":     {"size_pt": 11, "weight": "regular",  "font": "body",    "line_height": 1.5},
        "body-sm":  {"size_pt": 9,  "weight": "regular",  "font": "body",    "line_height": 1.5},
        "caption":  {"size_pt": 8,  "weight": "regular",  "font": "body",    "line_height": 1.4},
        "overline": {"size_pt": 8,  "weight": "bold",    "font": "body",    "line_height": 1.4, "transform": "uppercase"},
        "code":     {"size_pt": 10, "weight": "regular",  "font": "mono",    "line_height": 1.5},
    },
}


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
        "tokens": _DEFAULT_TOKENS,
        "defaults": {"page_format": "A4"},
        "_base_path": str(fallback_dir),
        "_fallback": True,
    }


def register_fonts(manifest: dict):
    """Register all brand fonts with reportlab for direct canvas use (compose.py zones).

    Returns dict of {role: {variant: font_name}} for registered fonts.
    xhtml2pdf uses its own @font-face CSS mechanism (see build_stylesheet).
    """
    from reportlab.lib.fonts import addMapping
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    base = manifest["_base_path"]
    fonts = manifest.get("fonts", {})
    registered = {}

    for role, variants in fonts.items():
        if isinstance(variants, dict):
            registered[role] = {}
            for variant, rel_path in variants.items():
                font_path = os.path.join(base, rel_path) if not os.path.isabs(rel_path) else rel_path
                if os.path.exists(font_path) and os.path.getsize(font_path) > 0:
                    font_name = f"Brand-{role}-{variant}"
                    try:
                        pdfmetrics.registerFont(TTFont(font_name, font_path))
                        registered[role][variant] = font_name
                    except Exception as e:
                        print(f"Warning: Could not register font {font_name}: {e}", file=sys.stderr)

    for role, variants in registered.items():
        family_name = f"Brand-{role}"
        regular = variants.get("regular")
        bold = variants.get("bold")
        italic = variants.get("italic")
        bold_italic = variants.get("bold_italic")

        if regular:
            addMapping(family_name, 0, 0, regular)
        if bold:
            addMapping(family_name, 1, 0, bold)
        if italic:
            addMapping(family_name, 0, 1, italic)
        if bold_italic:
            addMapping(family_name, 1, 1, bold_italic)

    return registered


def _resolve_font_name(font_role: str, weight: str) -> str:
    """Map a font role + weight to the registered reportlab font name."""
    if weight == "bold":
        return f"Brand-{font_role}-bold"
    return f"Brand-{font_role}-regular"


def _build_font_face_css(manifest: dict) -> str:
    """Generate @font-face CSS declarations for xhtml2pdf.

    xhtml2pdf needs @font-face with src: url() to register fonts in its own
    font list. The font-family names use 'Brand-{role}' convention.
    """
    base = manifest["_base_path"]
    fonts = manifest.get("fonts", {})
    rules = []

    weight_map = {"regular": "normal", "bold": "bold"}
    style_map = {"regular": "normal", "bold": "normal", "italic": "italic", "bold_italic": "italic"}
    weight_map_bi = {"bold_italic": "bold"}

    for role, variants in fonts.items():
        if not isinstance(variants, dict):
            continue
        family = f"Brand-{role}"
        for variant, rel_path in variants.items():
            font_path = os.path.join(base, rel_path) if not os.path.isabs(rel_path) else rel_path
            if not os.path.exists(font_path) or os.path.getsize(font_path) == 0:
                continue
            fw = weight_map_bi.get(variant, weight_map.get(variant, "normal"))
            fs = style_map.get(variant, "normal")
            rules.append(
                f"@font-face {{\n"
                f"  font-family: {family};\n"
                f"  src: url({font_path});\n"
                f"  font-weight: {fw};\n"
                f"  font-style: {fs};\n"
                f"}}"
            )

    return "\n".join(rules)


def build_stylesheet(manifest: dict, css_path: str = None) -> str:
    """Build CSS stylesheet from brand tokens, with @font-face and token-derived overrides."""
    tokens = manifest.get("tokens", _DEFAULT_TOKENS)
    colors = tokens.get("colors", _DEFAULT_TOKENS["colors"])
    type_scale = tokens.get("type_scale", _DEFAULT_TOKENS["type_scale"])

    # 1. @font-face declarations for xhtml2pdf
    font_face_css = _build_font_face_css(manifest)

    # 2. Load base.css structural template
    base_css_path = css_path or str(Path(__file__).parent.parent / "assets" / "css" / "base.css")
    base_css = ""
    if os.path.exists(base_css_path):
        with open(base_css_path) as f:
            base_css = f.read()

    # 3. Token-derived overrides (appended last so they win)
    fonts_available = manifest.get("fonts", {})
    body_role = "body" if "body" in fonts_available else "heading"
    heading_role = "heading" if "heading" in fonts_available else body_role
    mono_role = "mono" if "mono" in fonts_available else body_role

    body_ts = type_scale.get("body", {})
    h1_ts = type_scale.get("h1", {})
    h2_ts = type_scale.get("h2", {})
    h3_ts = type_scale.get("h3", {})
    h4_ts = type_scale.get("h4", {})
    code_ts = type_scale.get("code", {})

    overrides = f"""/* Brand token overrides — auto-generated */
body {{
  font-family: Brand-{body_role};
  font-size: {body_ts.get("size_pt", 11)}pt;
  color: {colors.get("text-body", "#1A1A1A")};
  line-height: {body_ts.get("line_height", 1.5)};
}}
h1, h2, h3, h4 {{
  font-family: Brand-{heading_role};
  font-weight: bold;
  color: {colors.get("text-heading", "#1A1A1A")};
}}
h1 {{ font-size: {h1_ts.get("size_pt", 32)}pt; line-height: {h1_ts.get("line_height", 1.15)}; }}
h2 {{ font-size: {h2_ts.get("size_pt", 24)}pt; line-height: {h2_ts.get("line_height", 1.2)}; }}
h3 {{ font-size: {h3_ts.get("size_pt", 18)}pt; line-height: {h3_ts.get("line_height", 1.25)}; }}
h4 {{ font-size: {h4_ts.get("size_pt", 14)}pt; line-height: {h4_ts.get("line_height", 1.3)}; }}
a {{ color: {colors.get("link", "#2E7D8C")}; }}
code, pre {{ font-family: Brand-{mono_role}; font-size: {code_ts.get("size_pt", 10)}pt; }}
blockquote {{ border-left-color: {colors.get("highlight", "#E8A838")}; }}
pre {{ border-left-color: {colors.get("highlight", "#E8A838")}; }}
th {{ border-bottom-color: {colors.get("border-strong", "#4A4A4A")}; }}
td {{ border-bottom-color: {colors.get("border-default", "#B0B0B0")}; }}
"""

    return font_face_css + "\n" + base_css + "\n" + overrides


def _insert_section_breaks(html: str) -> str:
    """Insert page breaks before h1 headings (except the first).

    Without this, xhtml2pdf renders all content as a continuous flow and
    section headings can land mid-page. Adding an explicit page-break-before
    ensures each top-level section starts on a fresh page.

    We skip the first h1 to avoid a blank leading page.
    """
    import re
    h1_re = re.compile(r'(<h1[\s>])')
    parts = h1_re.split(html)
    # split produces: [before_first_h1, '<h1', after, '<h1', after, ...]
    result = []
    h1_count = 0
    for part in parts:
        if h1_re.match(part):
            h1_count += 1
            if h1_count > 1:
                result.append('<div style="page-break-before: always;"></div>')
        result.append(part)
    return ''.join(result)


def render_html_to_pdf(html: str, output_path: str, manifest: dict, page_format: str = "A4", debug: bool = False):
    """Render HTML content to PDF pages."""
    from xhtml2pdf import pisa

    html = _insert_section_breaks(html)
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
