---
name: brand-decathlon
description: Brand kit for Decathlon. Provides design tokens (colors, typography, spacing), Inter font files, logo variants, and PDF page templates. Use whenever generating documents, presentations, or web pages for the Decathlon brand.
allowed-tools: Bash, Read, Write
license: MIT
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

### Imagery Guidelines

- **Style**: Professional reportage — natural, in-situation photography
- **Color treatment**: Full-color, natural light
- **Corner radius**: 0pt (no rounded corners)
- **Subjects**: Sport activities, action photography, diverse participants
- **Avoid**: Extreme situations, studio photography, stock-photo poses
- **AI prompt prefix**: `authentic sports reportage, natural light, dynamic composition, diverse participants, real-world setting, action photography, no rounded corners`

### Chart Guidelines

- **Primary palette**: Blue/purple (#3643BA), green accent (#7AFFA6), then semantic colors
- **Sequential**: Light-to-dark blue/purple gradient (7 stops)
- **Diverging**: Red ↔ Green through neutral gray
- **Highlight color**: #7AFFA6 (green accent) on #212121 contrast
- **Figure background**: White (#FFFFFF)
- Charts use brand typography tokens (h3 for titles, body-sm for axis labels, caption for ticks/legends)

## Usage with PDF Factory

1. Pass this skill's directory path as `--brand` to render.py and compose.py
2. Scripts read `assets/manifest.json` for fonts, logos, templates, and tokens
3. The `manifest.json["tokens"]` section drives all styling — colors and type scale
4. Zone overlays on covers/dividers use tokens for font, size, color, and alignment
5. SVG logos from `assets/logos/` are rendered as vectors on cover pages
6. Content pages are styled via dynamically generated CSS from the same tokens

Keep `manifest.json["tokens"]` in sync with `references/tokens.md`.
