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

    return manifest, zones, str(assets_dir)


def load_metadata(metadata_path: str) -> dict:
    """Load document metadata from JSON."""
    with open(metadata_path) as f:
        return json.load(f)


def create_zone_overlay(zones_def: dict, metadata: dict, page_size: tuple) -> bytes:
    """Create a PDF overlay with text placed in zone positions using reportlab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    buf = io.BytesIO()
    width, height = page_size
    c = canvas.Canvas(buf, pagesize=(width, height))

    zone_to_meta = {
        "title": metadata.get("title", ""),
        "subtitle": metadata.get("subtitle", ""),
        "date": metadata.get("date", "").upper(),
        "author": metadata.get("author", ""),
    }

    for zone_name, zone_spec in zones_def.get("zones", {}).items():
        if zone_spec.get("type") == "image":
            continue
        text = zone_to_meta.get(zone_name, "")
        if not text:
            continue

        x = zone_spec["x"]
        y = height - zone_spec["y"] - zone_spec["height"]
        c.setFont("Helvetica", 12)
        c.drawString(x, y, text)

    c.save()
    buf.seek(0)
    return buf.read()


def compose_document(brand_path: str, content_path: str, metadata_path: str, output_path: str):
    """Compose final PDF from content pages and brand templates."""
    from pypdf import PdfReader, PdfWriter

    manifest, zones, assets_dir = load_brand_assets(brand_path)
    metadata = load_metadata(metadata_path)
    templates_dir = os.path.join(assets_dir, "templates", "pdf")

    writer = PdfWriter()
    content_reader = PdfReader(content_path)

    # 1. Front cover
    cover_front_path = os.path.join(templates_dir, "cover-front.pdf")
    if os.path.exists(cover_front_path) and os.path.getsize(cover_front_path) > 0:
        cover_reader = PdfReader(cover_front_path)
        cover_page = cover_reader.pages[0]

        if "cover-front" in zones:
            zone_def = zones["cover-front"]
            page_size = tuple(zone_def.get("page_size", [595, 842]))
            overlay_bytes = create_zone_overlay(zone_def, metadata, page_size)
            overlay_reader = PdfReader(io.BytesIO(overlay_bytes))
            if overlay_reader.pages:
                cover_page.merge_page(overlay_reader.pages[0])

        writer.add_page(cover_page)

    # 2. Content pages with headers and footers
    sections = {s["page"]: s["title"] for s in metadata.get("sections", [])}

    for i, page in enumerate(content_reader.pages):
        page_num = i + 1

        # Insert section divider if this page starts a new section
        if page_num in sections:
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
                    )
                    overlay_reader = PdfReader(io.BytesIO(overlay_bytes))
                    if overlay_reader.pages:
                        divider_page.merge_page(overlay_reader.pages[0])

                writer.add_page(divider_page)

        # Merge content onto page-content template
        template_path = os.path.join(templates_dir, "page-content.pdf")
        if os.path.exists(template_path) and os.path.getsize(template_path) > 0:
            template_reader = PdfReader(template_path)
            template_page = template_reader.pages[0]
            template_page.merge_page(page)
            writer.add_page(template_page)
        else:
            writer.add_page(page)

    # 3. Back cover
    cover_back_path = os.path.join(templates_dir, "cover-back.pdf")
    if os.path.exists(cover_back_path) and os.path.getsize(cover_back_path) > 0:
        back_reader = PdfReader(cover_back_path)
        writer.add_page(back_reader.pages[0])

    # Write final PDF
    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"Composed final document: {output_path} ({len(writer.pages)} pages)")


def main():
    parser = argparse.ArgumentParser(description="Compose final PDF from content and brand templates")
    parser.add_argument("--brand", required=True, help="Path to brand kit skill directory")
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
