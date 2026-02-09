#!/usr/bin/env python3
"""Page assembly: merge content pages onto brand template pages.

Usage:
    python compose.py --brand <brand-kit-path> --content <content-pages.pdf> --metadata <metadata.json> --output <final.pdf>

Assembles the final document by:
1. Adding front cover with metadata in zones
2. Generating TOC if sections are defined
3. Merging content pages onto page-content template
4. Inserting section dividers at section boundaries
5. Adding back cover
"""
import argparse
import io
import json
import os
import sys
from pathlib import Path

# Import register_fonts and default tokens from render.py (same package)
sys.path.insert(0, str(Path(__file__).parent))
from render import _DEFAULT_TOKENS, register_fonts


def load_brand_assets(brand_path: str) -> tuple:
    """Load manifest and zones from brand kit."""
    brand_dir = Path(brand_path)
    assets_dir = brand_dir / "assets"

    manifest_path = assets_dir / "manifest.json"
    zones_path = assets_dir / "templates" / "pdf" / "zones.json"

    if not manifest_path.exists():
        print(f"Error: Manifest not found at {manifest_path}", file=sys.stderr)
        sys.exit(1)
    if not zones_path.exists():
        print(f"Error: Zones not found at {zones_path}", file=sys.stderr)
        sys.exit(1)

    with open(manifest_path) as f:
        manifest = json.load(f)
    with open(zones_path) as f:
        zones = json.load(f)

    manifest["_base_path"] = str(assets_dir)
    return manifest, zones, str(assets_dir)


def load_fallback_compose() -> tuple:
    """Return minimal manifest and empty zones for fallback (no brand) mode."""
    fallback_dir = Path(__file__).parent.parent / "assets" / "fallback"
    manifest = {
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
    return manifest, {}, str(fallback_dir)


def load_metadata(metadata_path: str) -> dict:
    """Load document metadata from JSON."""
    with open(metadata_path) as f:
        return json.load(f)


def _resolve_font_name(font_role: str, weight: str) -> str:
    """Map a font role + weight to the registered reportlab font name."""
    if weight == "bold":
        return f"Brand-{font_role}-bold"
    return f"Brand-{font_role}-regular"


def _hex_to_color(hex_str: str):
    """Convert hex color string to reportlab Color."""
    from reportlab.lib.colors import HexColor
    return HexColor(hex_str)


def create_zone_overlay(zones_def: dict, metadata: dict, page_size: tuple, manifest: dict, assets_dir: str) -> bytes:
    """Create a PDF overlay with text/images placed in zone positions using reportlab."""
    from reportlab.pdfgen import canvas

    tokens = manifest.get("tokens", _DEFAULT_TOKENS)
    colors = tokens.get("colors", _DEFAULT_TOKENS["colors"])
    type_scale = tokens.get("type_scale", _DEFAULT_TOKENS["type_scale"])

    buf = io.BytesIO()
    width, height = page_size
    c = canvas.Canvas(buf, pagesize=(width, height))

    zone_to_meta = {
        "title": metadata.get("title", ""),
        "subtitle": metadata.get("subtitle", ""),
        "date": metadata.get("date", ""),
        "author": metadata.get("author", ""),
        "section_number": metadata.get("section_number", ""),
        "section_title": metadata.get("section_title", ""),
    }

    for zone_name, zone_spec in zones_def.get("zones", {}).items():
        # Handle image zones (SVG logos)
        if zone_spec.get("type") == "image":
            svg_source = zone_spec.get("source", "")
            if not svg_source:
                continue
            svg_path = os.path.join(assets_dir, "logos", svg_source)
            if not os.path.exists(svg_path):
                continue
            try:
                from svglib.svglib import svg2rlg
                from reportlab.graphics import renderPDF

                drawing = svg2rlg(svg_path)
                if drawing:
                    zw = zone_spec.get("width", 120)
                    zh = zone_spec.get("height", 40)
                    sx = zw / drawing.width
                    sy = zh / drawing.height
                    scale = min(sx, sy)
                    drawing.width *= scale
                    drawing.height *= scale
                    drawing.scale(scale, scale)
                    draw_x = zone_spec["x"]
                    draw_y = height - zone_spec["y"] - zh
                    renderPDF.draw(drawing, c, draw_x, draw_y)
            except Exception as e:
                print(f"Warning: Could not render SVG {svg_source}: {e}", file=sys.stderr)
            continue

        # Text zones
        text = zone_to_meta.get(zone_name, "")
        if not text:
            continue

        # Resolve style from type_scale
        style_name = zone_spec.get("style", "body")
        style = type_scale.get(style_name, type_scale.get("body", {}))
        size_pt = style.get("size_pt", 11)
        weight = style.get("weight", "regular")
        font_role = style.get("font", "body")
        font_name = _resolve_font_name(font_role, weight)

        # Apply text transform
        if style.get("transform") == "uppercase":
            text = text.upper()

        # Resolve color from color role
        color_role = zone_spec.get("color_role", "text-body")
        color_hex = colors.get(color_role, "#000000")

        x = zone_spec["x"]
        zone_width = zone_spec.get("width", 495)
        zone_height = zone_spec.get("height", 40)
        align = zone_spec.get("align", "left")

        # Baseline at top of zone (descend by font size from zone top)
        y = height - zone_spec["y"] - size_pt

        actual_font = font_name
        try:
            c.setFont(font_name, size_pt)
        except KeyError:
            actual_font = "Helvetica"
            c.setFont(actual_font, size_pt)

        # Auto-shrink if text overflows zone width
        text_width = c.stringWidth(text, actual_font, size_pt)
        while text_width > zone_width and size_pt > 6:
            size_pt -= 0.5
            c.setFont(actual_font, size_pt)
            text_width = c.stringWidth(text, actual_font, size_pt)

        c.setFillColor(_hex_to_color(color_hex))

        if align == "center":
            c.drawCentredString(x + zone_width / 2, y, text)
        elif align == "right":
            c.drawRightString(x + zone_width, y, text)
        else:
            c.drawString(x, y, text)

    c.save()
    buf.seek(0)
    return buf.read()


def compose_document(brand_path: str, content_path: str, metadata_path: str, output_path: str):
    """Compose final PDF from content pages and brand templates."""
    from pypdf import PdfReader, PdfWriter

    if brand_path:
        manifest, zones, assets_dir = load_brand_assets(brand_path)
    else:
        manifest, zones, assets_dir = load_fallback_compose()

    # Register brand fonts for zone overlay rendering
    register_fonts(manifest)

    metadata = load_metadata(metadata_path)

    writer = PdfWriter()
    content_reader = PdfReader(content_path)

    is_fallback = manifest.get("_fallback", False)
    templates_dir = os.path.join(assets_dir, "templates", "pdf") if not is_fallback else None

    # 1. Front cover (skip in fallback mode)
    if not is_fallback and templates_dir:
        cover_front_path = os.path.join(templates_dir, "cover-front.pdf")
        if os.path.exists(cover_front_path) and os.path.getsize(cover_front_path) > 0:
            cover_reader = PdfReader(cover_front_path)
            cover_page = cover_reader.pages[0]

            if "cover-front" in zones:
                zone_def = zones["cover-front"]
                page_size = tuple(zone_def.get("page_size", [595, 842]))
                overlay_bytes = create_zone_overlay(zone_def, metadata, page_size, manifest, assets_dir)
                overlay_reader = PdfReader(io.BytesIO(overlay_bytes))
                if overlay_reader.pages:
                    cover_page.merge_page(overlay_reader.pages[0])

            writer.add_page(cover_page)

    # 2. Detect section boundaries from rendered content pages.
    #    render.py inserts page breaks before each h1, so the first line of
    #    a page that starts a new section will contain the section heading.
    #    We match these against metadata section titles to build an accurate
    #    page→title map instead of trusting metadata page numbers (which are
    #    estimates that may drift from the actual rendered layout).
    meta_sections = metadata.get("sections", [])
    section_titles = [s["title"] for s in meta_sections]

    sections = {}  # {content_page_num: title}
    for i, page in enumerate(content_reader.pages):
        page_text = (page.extract_text() or "").strip()
        # Check first ~200 chars to handle headings that wrap across lines
        head = " ".join(page_text[:200].split())
        for title in section_titles:
            if not title:
                continue
            # Match if page starts with the section title (exact or wrapped)
            if title in head or head.startswith(title):
                sections[i + 1] = title
                break

    # Fallback: if detection found nothing, use metadata page numbers directly
    if not sections and meta_sections:
        total_pages = len(content_reader.pages)
        sections = {s["page"]: s["title"] for s in meta_sections if s["page"] <= total_pages}

    for i, page in enumerate(content_reader.pages):
        page_num = i + 1

        # Insert section divider if this page starts a new section (skip in fallback)
        if not is_fallback and page_num in sections and templates_dir:
            divider_path = os.path.join(templates_dir, "section-divider.pdf")
            if os.path.exists(divider_path) and os.path.getsize(divider_path) > 0:
                divider_reader = PdfReader(divider_path)
                divider_page = divider_reader.pages[0]

                if "section-divider" in zones:
                    section_meta = {
                        "section_number": str(list(sections.keys()).index(page_num) + 1),
                        "section_title": sections[page_num],
                    }
                    zone_def = zones["section-divider"]
                    page_size = tuple(zone_def.get("page_size", [595, 842]))
                    overlay_bytes = create_zone_overlay(
                        {"zones": zone_def.get("zones", {})},
                        section_meta,
                        page_size,
                        manifest,
                        assets_dir,
                    )
                    overlay_reader = PdfReader(io.BytesIO(overlay_bytes))
                    if overlay_reader.pages:
                        divider_page.merge_page(overlay_reader.pages[0])

                writer.add_page(divider_page)

        # Merge content onto page-content template (or pass through in fallback)
        if not is_fallback and templates_dir:
            template_path = os.path.join(templates_dir, "page-content.pdf")
            if os.path.exists(template_path) and os.path.getsize(template_path) > 0:
                template_reader = PdfReader(template_path)
                template_page = template_reader.pages[0]
                template_page.merge_page(page)
                writer.add_page(template_page)
            else:
                writer.add_page(page)
        else:
            writer.add_page(page)

    # 3. Back cover (skip in fallback mode)
    if not is_fallback and templates_dir:
        cover_back_path = os.path.join(templates_dir, "cover-back.pdf")
        if os.path.exists(cover_back_path) and os.path.getsize(cover_back_path) > 0:
            back_reader = PdfReader(cover_back_path)
            back_page = back_reader.pages[0]

            # Render back cover zones (e.g. logo)
            if "cover-back" in zones:
                zone_def = zones["cover-back"]
                page_size = tuple(zone_def.get("page_size", [595, 842]))
                overlay_bytes = create_zone_overlay(zone_def, {}, page_size, manifest, assets_dir)
                overlay_reader = PdfReader(io.BytesIO(overlay_bytes))
                if overlay_reader.pages:
                    back_page.merge_page(overlay_reader.pages[0])

            writer.add_page(back_page)

    # 4. Set PDF metadata
    writer.add_metadata({
        "/Title": metadata.get("title", ""),
        "/Author": metadata.get("author", ""),
        "/Subject": metadata.get("subtitle", ""),
        "/Creator": "pdf-factory",
    })

    # Write final PDF
    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"Composed final document: {output_path} ({len(writer.pages)} pages)")


def main():
    parser = argparse.ArgumentParser(description="Compose final PDF from content and brand templates")
    parser.add_argument("--brand", required=False, help="Path to brand kit skill directory")
    parser.add_argument("--content", required=True, help="Path to rendered content pages PDF")
    parser.add_argument("--metadata", required=True, help="Path to metadata JSON file")
    parser.add_argument("--output", required=True, help="Output PDF path")
    args = parser.parse_args()

    for path, label in [(args.content, "Content PDF"), (args.metadata, "Metadata JSON")]:
        if not os.path.exists(path):
            print(f"Error: {label} not found: {path}", file=sys.stderr)
            sys.exit(1)

    compose_document(args.brand, args.content, args.metadata, args.output)


if __name__ == "__main__":
    main()
