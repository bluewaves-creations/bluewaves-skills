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


def _apply_corner_radius(img_path: str, radius_pt: float, output_path: str, dpi: int = 150):
    """Apply rounded corners to a raster image using Pillow.

    Converts pt radius to pixels based on DPI, creates RGBA image with
    transparent rounded corners. Only activates when radius_pt > 0.
    """
    from PIL import Image, ImageChops, ImageDraw

    radius_px = int(radius_pt * dpi / 72)
    if radius_px < 1:
        return img_path

    img = Image.open(img_path).convert("RGBA")
    w, h = img.size

    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (w, h)], radius=radius_px, fill=255)

    # Multiply with original alpha to preserve existing transparency (e.g. logos)
    original_alpha = img.split()[3]
    combined = ImageChops.multiply(original_alpha, mask)
    img.putalpha(combined)
    img.save(output_path, "PNG")
    return output_path


def _preprocess_svg_images(html: str, manifest: dict, work_dir: str) -> str:
    """Convert SVG references in HTML to high-DPI PNG for xhtml2pdf compatibility.

    Handles both <img src="*.svg"> references and inline <svg>...</svg> blocks.
    Uses svglib + reportlab (already installed) for conversion at 2x scale.
    Falls back gracefully on conversion failure (leaves original tag intact).
    """
    import re
    import tempfile
    from pathlib import Path

    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM
    except ImportError:
        return html

    svg_count = 0

    # Handle <img src="*.svg"> references
    def replace_svg_img(match):
        nonlocal svg_count
        full_tag = match.group(0)
        src = match.group(1)

        svg_path = src
        if not os.path.isabs(svg_path):
            svg_path = os.path.join(work_dir, svg_path)

        if not os.path.exists(svg_path):
            return full_tag

        try:
            drawing = svg2rlg(svg_path)
            if drawing is None:
                return full_tag
            svg_count += 1
            png_path = os.path.join(work_dir, f"_svg2png_{svg_count}.png")
            renderPM.drawToFile(drawing, png_path, fmt="PNG", dpi=300)
            return full_tag.replace(src, png_path)
        except Exception:
            return full_tag

    html = re.sub(r'<img\s[^>]*src="([^"]+\.svg)"[^>]*>', replace_svg_img, html)

    # Handle inline <svg>...</svg> blocks
    def replace_inline_svg(match):
        nonlocal svg_count
        svg_content = match.group(0)

        try:
            svg_count += 1
            svg_tmp = os.path.join(work_dir, f"_inline_svg_{svg_count}.svg")
            png_path = os.path.join(work_dir, f"_inline_svg_{svg_count}.png")

            with open(svg_tmp, "w") as f:
                f.write(svg_content)

            drawing = svg2rlg(svg_tmp)
            if drawing is None:
                return svg_content
            renderPM.drawToFile(drawing, png_path, fmt="PNG", dpi=300)
            return f'<img src="{png_path}" />'
        except Exception:
            return svg_content

    html = re.sub(r'<svg[\s>].*?</svg>', replace_inline_svg, html, flags=re.DOTALL)

    return html


def _preprocess_images(html: str, manifest: dict, work_dir: str) -> str:
    """Apply corner radius to raster images based on brand imagery tokens."""
    import re

    tokens = manifest.get("tokens", {})
    imagery = tokens.get("imagery", {})
    radius_pt = imagery.get("corner_radius_pt", 0)

    if radius_pt <= 0:
        return html

    img_count = 0

    def apply_radius(match):
        nonlocal img_count
        full_tag = match.group(0)
        src = match.group(1)

        # Skip SVG placeholders and data URIs
        if src.endswith(".svg") or src.startswith("data:"):
            return full_tag

        img_path = src if os.path.isabs(src) else os.path.join(work_dir, src)
        if not os.path.exists(img_path):
            return full_tag

        try:
            img_count += 1
            rounded_path = os.path.join(work_dir, f"_rounded_{img_count}.png")
            _apply_corner_radius(img_path, radius_pt, rounded_path)
            return full_tag.replace(src, rounded_path)
        except Exception:
            return full_tag

    html = re.sub(r'<img\s[^>]*src="([^"]+)"[^>]*>', apply_radius, html)
    return html


def _preprocess_figures(html: str) -> str:
    """Convert <figure>/<figcaption> to <div>/<p> for xhtml2pdf compatibility.

    xhtml2pdf does not treat HTML5 <figure> and <figcaption> as block-level
    elements — it renders them inline regardless of CSS display rules.
    Replacing with <div class="figure"> and <p class="figcaption"> ensures
    block layout and allows CSS styling via class selectors.

    Uses regex to handle tags with optional attributes (e.g. <figure class="chart">).
    """
    import re
    html = re.sub(r'<figure(\s[^>]*)?>',  r'<div class="figure"\1>', html)
    html = html.replace("</figure>", "</div>")
    html = re.sub(r'<figcaption(\s[^>]*)?>',  r'<p class="figcaption"\1>', html)
    html = html.replace("</figcaption>", "</p>")
    return html


def _preprocess_code_blocks(html: str) -> str:
    """Replace newlines with <br/> inside <pre><code> blocks.

    xhtml2pdf's white-space: pre-wrap does not reliably preserve \\n inside
    <code> elements. Converting newlines to explicit <br/> tags ensures
    line-per-line formatting in rendered PDF output.

    Preserves any attributes on <pre> and <code> tags, and strips leading/
    trailing newlines to avoid spurious <br/> whitespace.
    """
    import re

    def fix_newlines(match):
        pre_attrs = match.group(1) or ""
        code_attrs = match.group(2) or ""
        content = match.group(3)
        content = content.strip("\n")
        content = content.replace("\n", "<br/>")
        return f"<pre{pre_attrs}><code{code_attrs}>{content}</code></pre>"

    return re.sub(
        r"<pre(\s[^>]*)?><code(\s[^>]*)?>(.*?)</code></pre>",
        fix_newlines, html, flags=re.DOTALL,
    )


def _preprocess_image_widths(html: str) -> str:
    """Convert HTML width attributes on img tags to pt-based inline styles.

    xhtml2pdf interprets bare numeric width attributes as pixels, but content
    authors specify them in points (matching PDF page geometry). Converting to
    explicit 'pt' units ensures images render at the intended size.
    """
    import re

    def convert_width(match):
        full_tag = match.group(0)
        width_val = match.group(1)
        # Remove the width attribute
        tag = re.sub(r'\s+width="' + re.escape(width_val) + '"', '', full_tag)
        # Add pt-based width as inline style
        if 'style="' in tag:
            tag = tag.replace('style="', f'style="width: {width_val}pt; ')
        else:
            tag = tag.replace("<img ", f'<img style="width: {width_val}pt" ')
        return tag

    return re.sub(r'<img\s[^>]*width="(\d+)"[^>]*>', convert_width, html)


def render_html_to_pdf(html: str, output_path: str, manifest: dict, page_format: str = "A4", debug: bool = False):
    """Render HTML content to PDF pages."""
    from xhtml2pdf import pisa

    html = _insert_section_breaks(html)
    html = _preprocess_figures(html)
    html = _preprocess_code_blocks(html)
    html = _preprocess_image_widths(html)

    # Preprocessing: SVG conversion and image corner radius
    work_dir = os.path.dirname(os.path.abspath(output_path))
    html = _preprocess_svg_images(html, manifest, work_dir)
    html = _preprocess_images(html, manifest, work_dir)

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
