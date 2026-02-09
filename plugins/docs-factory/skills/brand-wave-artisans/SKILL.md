---
name: brand-wave-artisans
description: >
  Brand kit for Wave Artisans. Provides design tokens (colors, typography,
  spacing), Nunito Sans font files, logo variants, PDF page templates
  with content zones, and decorative patterns. This skill should be used
  whenever generating documents, presentations, web pages, or images for
  Wave Artisans. It triggers on requests mentioning Wave Artisans brand,
  Wave Artisans documents, Wave Artisans styling, or Wave Artisans
  identity. Pairs with the pdf-factory skill for PDF output.
allowed-tools: Bash, Read, Write
---
# Wave Artisans Brand Kit

## Quick Reference

- **Palette**: Gray-driven — no single primary color
- **Background**: #F5F5F7 (subtle light gray)
- **Body font**: Nunito Sans (assets/fonts/body.ttf)
- **Heading font**: Nunito Sans Bold (assets/fonts/heading-bold.ttf)
- **Page format**: A4
- **Text color**: #1C1C1E (never pure black)

## Assets

Use the manifest at `assets/manifest.json` as the programmatic entry point.

Replace placeholder files in `assets/` with actual brand assets before production use.

### Fonts

Four roles: heading, body, mono. All TTF files in `assets/fonts/`.

| Role | Family | Weight | File |
|------|--------|--------|------|
| Heading | Nunito Sans | regular | heading.ttf |
| Heading | Nunito Sans | bold | heading-bold.ttf |
| Body | Nunito Sans | regular | body.ttf |
| Body | Nunito Sans | italic | body-italic.ttf |
| Body | Nunito Sans | bold | body-bold.ttf |
| Body | Nunito Sans | bold italic | body-bold-italic.ttf |
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

- Nunito Sans for both headings (bold) and body (regular) — single-family harmony
- Gray-driven identity: no single primary color, the gray itself is the brand
- Subtle light gray backgrounds (#F5F5F7) with near-black text (#1C1C1E)
- Semantic colors used as-needed for accent and categorization
- Apple-minimalist: clean font hierarchy, no decorators/lines, perfect typography and spacing

## Usage with PDF Factory

1. Provide `assets/manifest.json` to the engine to discover available resources
2. Provide `assets/templates/pdf/zones.json` for content zone placement
3. Load font files from `assets/fonts/`
4. Merge content onto template PDFs from `assets/templates/pdf/`
