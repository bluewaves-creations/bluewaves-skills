---
name: brand-bluewaves
description: >
  Brand kit for Bluewaves. Provides design tokens (colors, typography,
  spacing), Merriweather font files, logo variants, PDF page templates
  with content zones, and decorative patterns. This skill should be used
  whenever generating documents, presentations, web pages, or images for
  Bluewaves. It triggers on requests mentioning Bluewaves brand, Bluewaves
  documents, Bluewaves styling, or Bluewaves identity. Pairs with the
  pdf-factory skill for PDF output.
allowed-tools: Bash, Read, Write
---
# Bluewaves Brand Kit

## Quick Reference

- **Primary color**: #B78A66 (brown sand)
- **Accent 1**: #00D2E0 (teal ocean) — use sparingly
- **Accent 2**: #FF375F (sun red) — use sparingly
- **Body font**: Merriweather (assets/fonts/body.ttf)
- **Heading font**: Merriweather Bold (assets/fonts/heading-bold.ttf)
- **Page format**: A4
- **Text color**: #2C2C2C (never pure black)
- **Background**: white

## Assets

Use the manifest at `assets/manifest.json` as the programmatic entry point.

Replace placeholder files in `assets/` with actual brand assets before production use.

### Fonts

Four roles: heading, body, mono. All TTF files in `assets/fonts/`.

| Role | Family | Weight | File |
|------|--------|--------|------|
| Heading | Merriweather | regular | heading.ttf |
| Heading | Merriweather | bold | heading-bold.ttf |
| Body | Merriweather | regular | body.ttf |
| Body | Merriweather | italic | body-italic.ttf |
| Body | Merriweather | bold | body-bold.ttf |
| Body | Merriweather | bold italic | body-bold-italic.ttf |
| Mono | Fira Code | regular | mono.ttf |

### Logos

Variants: full lockup and mark, each in color and white.
Files in `assets/logos/`. Use `logo-full-color.svg` as default.

| Variant | Color | White |
|---------|-------|-------|
| Full lockup | logo-full-color.svg/.png | logo-full-white.svg/.png |
| Mark | logo-mark-color.svg/.png | logo-mark-white.svg/.png |
| Favicon | favicon.png (512x512) | — |
| Wordmark | wordmark.svg | — |

### PDF Templates

Pre-designed pages in `assets/templates/pdf/`. Content placement
defined in `assets/templates/pdf/zones.json`.

Select from templates: cover-front, cover-back, page-content, page-blank,
section-divider, color-primary, color-accent.

### Patterns

Find decorative assets in `assets/patterns/`: pattern-01.svg/.png, divider-line.svg.

## Design Tokens

For full token definitions (color palette, type scale, spacing grid,
shadows), see [references/tokens.md](references/tokens.md).

### Key Design Principles

- Merriweather for both headings (bold) and body (regular) — single-family harmony
- Brown sand primary carries the identity; teal and red accents used sparingly
- White backgrounds with warm neutral text (#2C2C2C)
- Apple-minimalist: clean font hierarchy, no decorators/lines, perfect typography and spacing

## Usage with PDF Factory

1. Provide `assets/manifest.json` to the engine to discover available resources
2. Provide `assets/templates/pdf/zones.json` for content zone placement
3. Load font files from `assets/fonts/`
4. Merge content onto template PDFs from `assets/templates/pdf/`
