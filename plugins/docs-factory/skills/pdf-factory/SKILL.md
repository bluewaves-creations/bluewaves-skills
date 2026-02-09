---
name: pdf-factory
description: >
  Production-grade PDF rendering engine. Converts markdown content into
  professionally typeset PDF documents using brand kit assets. Handles
  page composition, typography, grid layout, content flow, tables, code
  blocks, and images. This skill should be used whenever generating PDF
  documents, reports, proposals, or any paginated output. It triggers on
  requests mentioning PDF generation, document rendering, report creation,
  or paginated output.
  Requires a brand-* kit skill for branded output; falls back to minimal
  defaults without one.
allowed-tools: Bash, Read, Write
license: MIT
compatibility: Python 3.8+ with packages from scripts/install_deps.py
---
# PDF Factory

## Dependencies

Run before first use:

```bash
python3 scripts/install_deps.py
```

Required packages: xhtml2pdf, reportlab, pypdf, pyhanko, markdown, lxml,
pillow, html5lib, cssselect2, svglib, python-bidi, arabic-reshaper.

The installer uses `--no-deps` for svglib, rlpycairo, and xhtml2pdf to avoid
building the `pycairo` C extension (which requires the system `cairo` library).
If installation fails with cairo/meson errors, run manually:

    uv pip install --no-deps rlpycairo svglib xhtml2pdf

## Pipeline

Generate PDFs by following these steps in order:

1. **Resolve brand kit** — Locate brand-{slug} skill, read manifest.json and zones.json
2. **Parse markdown** — Convert source to HTML via `markdown` library
3. **Render content pages** — Run render.py to produce styled content pages
4. **Compose document** — Run compose.py to merge content with template pages
5. **Validate output** — Run validate_output.py, fix errors, repeat until pass
6. **Sign (optional)** — Apply digital signature via pyhanko

## How It Works

### Font Registration

The pipeline registers fonts at two levels:

1. **xhtml2pdf** (render.py) — Generates `@font-face` CSS declarations with absolute
   paths to TTF files. Font families use `Brand-{role}` names (e.g., `Brand-body`,
   `Brand-heading`, `Brand-mono`). xhtml2pdf resolves these via its own CSS engine.
   **Do not** use reportlab `TTFont()` names directly in CSS — xhtml2pdf ignores them.

2. **reportlab** (compose.py) — Registers `TTFont("Brand-{role}-{variant}", path)`
   and `addMapping()` for bold/italic. Used by zone overlays on cover/divider pages.

### Zone Overlays

Zone text on covers and dividers is rendered by compose.py using reportlab canvas,
NOT xhtml2pdf. Each zone in `zones.json` specifies:
- `style` → looks up `manifest.tokens.type_scale[style]` for size_pt, weight, font role
- `color_role` → looks up `manifest.tokens.colors[color_role]` for hex color
- `align` → left, center, or right
- `type: "image"` → renders SVG logo via svglib

Text auto-shrinks if it overflows the zone width.

### Section Page Breaks

render.py preprocesses the HTML via `_insert_section_breaks()`, which injects
`<div style="page-break-before: always;"></div>` before every `<h1>` except
the first. This is an HTML-level transformation, not a CSS rule. Do NOT add
`page-break-before` to h1 in base.css — that creates a blank first page.

compose.py auto-detects section boundaries by scanning the rendered content pages for
text matching the section titles in metadata.json. This means the `page` values in
metadata sections are only hints — compose.py will find the correct pages from the
rendered output. You still need section titles in metadata.json to be accurate.

### Orphan Title Prevention

base.css applies `-pdf-keep-with-next: true` to all headings (h1–h4). This is an
xhtml2pdf-specific property. The standard `page-break-after: avoid` is parsed
but NOT enforced by xhtml2pdf — do not use it.

### CSS Specifics

Heading spacing (margin-bottom): h1 16pt, h2 12pt, h3 8pt, h4 6pt.
List indentation: `padding-left: 14pt` on ul/ol.
Code/table background: `#F0F0F0` (base.css structural default, overridden by
brand token `background-alt` if different).

### Token Resolution

Scripts read tokens from `manifest.json["tokens"]`, not from `references/tokens.md`.
The `references/tokens.md` file is for Claude to understand the design system;
the `manifest.json["tokens"]` section is the machine-readable source for scripts.
Both must stay in sync.

## Step 1: Resolve Brand Kit

Locate the brand kit skill directory and read:
- `assets/manifest.json` — font paths, logo paths, template paths, tokens (colors + type_scale)
- `assets/templates/pdf/zones.json` — content zones for each template page

The `manifest.json["tokens"]` section is the machine-readable source of truth for all
color and typography values used by the pipeline scripts.

If no brand kit is specified, use fallback assets from `assets/fallback/`.

## Step 2: Parse Markdown

Convert source markdown to HTML:

```python
import markdown
html = markdown.markdown(source, extensions=[
    'tables', 'fenced_code', 'codehilite', 'toc', 'meta', 'attr_list'
])
```

Extract document metadata from markdown frontmatter:
- `title`, `subtitle`, `author`, `date` → cover page zones
- `sections` → section divider insertion

## Step 3: Render Content Pages

The `--brand` flag is optional. Without it, render.py uses fallback fonts and colors.

```bash
# With brand kit:
python3 scripts/render.py \
  --brand /path/to/brand-{slug} \
  --input content.html \
  --output content-pages.pdf

# Fallback (no brand kit):
python3 scripts/render.py \
  --input content.html \
  --output content-pages.pdf
```

For composition rules (grid, spacing, page breaks, widows/orphans), load
[references/composition.md](references/composition.md).

For element rendering details (headings, code blocks, tables, lists), load
[references/elements.md](references/elements.md).

## Step 4: Compose Document

The `--brand` flag is optional. Without it, compose.py produces content-only output
(no cover pages, section dividers, or zone overlays).

```bash
# With brand kit:
python3 scripts/compose.py \
  --brand /path/to/brand-{slug} \
  --content content-pages.pdf \
  --metadata metadata.json \
  --output final.pdf

# Fallback (no brand kit, metadata only):
python3 scripts/compose.py \
  --content content-pages.pdf \
  --metadata metadata.json \
  --output final.pdf
```

compose.py embeds title, author, and subtitle from metadata.json into the PDF info
dictionary.

Provide metadata.json with this structure:

```json
{
  "title": "Document Title",
  "subtitle": "Optional Subtitle",
  "author": "Author Name",
  "date": "February 9, 2026",
  "sections": [
    { "title": "Introduction", "page": 1 },
    { "title": "Analysis", "page": 5 }
  ]
}
```

## Step 5: Validate Output

```bash
python3 scripts/validate_output.py final.pdf --brand /path/to/brand-{slug}
```

If validation fails, check these common issues:
- **"Font not embedded"** — Verify font path in manifest matches actual file in assets/fonts/
- **"Page count 0"** — Verify render.py produced output; check input HTML is not empty
- **"Missing metadata"** — Ensure metadata.json contains title and author fields
- **"Brand font missing"** — Confirm all fonts declared in manifest exist on disk

Fix errors and re-run validation. Only proceed when all checks pass.

## Step 6: Sign (Optional)

Apply digital signature via pyhanko when required:

```python
from pyhanko.sign import signers
from pyhanko.keys import load_cert_from_pemder
# Requires a PKCS#12 certificate file (.p12/.pfx)
```

## Example

**Input markdown:**

```markdown
---
title: Q4 Performance Review
subtitle: Engineering Division
author: Jane Smith
date: January 2026
---

# Executive Summary

Revenue grew 23% year-over-year...

# Technical Achievements

## Infrastructure Scaling

We migrated 40 services to the new platform...
```

**Expected output (using brand-bluewaves):**

1. Cover page: `cover-front.pdf` template with "Q4 Performance Review" in title zone (display style, text-inverse), "Engineering Division" in subtitle zone, "JANUARY 2026" in date zone, Bluewaves logo in logo zone
2. Content pages: Body text on `page-content.pdf` template, heading font for h1/h2, body font for paragraphs, document title in header zone, page numbers in footer zone
3. Section dividers: `section-divider.pdf` template inserted before "Executive Summary" and "Technical Achievements" with section titles in zones
4. Back cover: `cover-back.pdf` template as final page

## Fallback Mode

When no brand kit is specified, the pipeline uses `assets/fallback/` assets:
- Colors: text `#1A1A1A`, headings `#1A1A1A`, muted `#7A7A7A`
- Fonts: Noto Sans (body/heading), Fira Code (code) — production fonts, not placeholders
- Layout: A4, 25mm margins, 11pt body
- No cover pages or section dividers in fallback mode
