---
name: brand-decathlon
description: >
  Brand kit for Decathlon. Provides design tokens (colors, typography,
  spacing), Inter font files, logo variants, PDF page templates with
  content zones, and decorative patterns. This skill should be used
  whenever generating documents, presentations, web pages, or images for
  Decathlon. It triggers on requests mentioning Decathlon brand, Decathlon
  documents, Decathlon styling, or Decathlon identity. Pairs with the
  pdf-factory skill for PDF output.
allowed-tools: Bash, Read, Write
---
# Decathlon Brand Kit

## Quick Reference

- **Primary color**: #3643BA (blue/purple)
- **Accent**: #7AFFA6 (green) — only on blue/dark backgrounds
- **Body font**: Inter (assets/fonts/body.ttf)
- **Heading font**: Inter Bold (assets/fonts/heading-bold.ttf)
- **Page format**: A4
- **Text color**: #212121 (never pure black)
- **Background**: white
- **No rounded corners**

## Assets

Use the manifest at `assets/manifest.json` as the programmatic entry point.

Replace placeholder files in `assets/` with actual brand assets before production use.

### Fonts

Four roles: heading, body, mono. All TTF files in `assets/fonts/`.

| Role | Family | Weight | File |
|------|--------|--------|------|
| Heading | Inter | regular | heading.ttf |
| Heading | Inter | bold | heading-bold.ttf |
| Body | Inter | regular | body.ttf |
| Body | Inter | italic | body-italic.ttf |
| Body | Inter | bold | body-bold.ttf |
| Body | Inter | bold italic | body-bold-italic.ttf |
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

- Inter for both headings (bold) and body (regular) — single-family harmony
- Blue/purple primary (#3643BA) carries the identity
- Green accent (#7AFFA6) only appears on primary blue or dark backgrounds
- White backgrounds with near-black text (#212121)
- No rounded corners on any element
- Apple-minimalist: clean font hierarchy, no decorators/lines, perfect typography and spacing

## Usage with PDF Factory

1. Provide `assets/manifest.json` to the engine to discover available resources
2. Provide `assets/templates/pdf/zones.json` for content zone placement
3. Load font files from `assets/fonts/`
4. Merge content onto template PDFs from `assets/templates/pdf/`
