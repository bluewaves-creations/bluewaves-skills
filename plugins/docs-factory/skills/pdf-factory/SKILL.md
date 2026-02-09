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
---
# PDF Factory

## Dependencies

Run before first use:

```bash
python3 scripts/install_deps.py
```

Required packages: xhtml2pdf, reportlab, pypdf, pyhanko, markdown, lxml,
pillow, html5lib, cssselect2, python-bidi, arabic-reshaper.

## Pipeline

Generate PDFs by following these steps in order:

1. **Resolve brand kit** — Locate brand-{slug} skill, read manifest.json and zones.json
2. **Parse markdown** — Convert source to HTML via `markdown` library
3. **Render content pages** — Run render.py to produce styled content pages
4. **Compose document** — Run compose.py to merge content with template pages
5. **Validate output** — Run validate_output.py, fix errors, repeat until pass
6. **Sign (optional)** — Apply digital signature via pyhanko

## Step 1: Resolve Brand Kit

Locate the brand kit skill directory and read:
- `assets/manifest.json` — font paths, logo paths, template paths, defaults
- `assets/templates/pdf/zones.json` — content zones for each template page

Load design tokens from `references/tokens.md` for color and typography values.

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

```bash
python3 scripts/render.py \
  --brand /path/to/brand-{slug} \
  --input content.html \
  --output content-pages.pdf
```

For composition rules (grid, spacing, page breaks, widows/orphans), load
[references/composition.md](references/composition.md).

For element rendering details (headings, code blocks, tables, lists), load
[references/elements.md](references/elements.md).

## Step 4: Compose Document

```bash
python3 scripts/compose.py \
  --brand /path/to/brand-{slug} \
  --content content-pages.pdf \
  --metadata metadata.json \
  --output final.pdf
```

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

When no brand kit is specified, use `assets/fallback/` assets with hardcoded defaults:
- Colors: text `#1A1A1A`, headings `#333333`, muted `#7A7A7A`
- Fonts: Noto Sans (body), Fira Code (code)
- Layout: A4, 25mm margins, 11pt body
