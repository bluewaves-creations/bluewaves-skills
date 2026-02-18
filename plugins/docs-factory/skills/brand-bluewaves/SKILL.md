---
name: brand-bluewaves
description: Brand kit for Bluewaves. Provides design tokens (colors, typography, spacing), Merriweather font files, logo variants, and PDF page templates. Use whenever generating documents, presentations, or web pages for the Bluewaves brand.
allowed-tools: Bash, Read, Write
license: MIT
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

### Imagery Guidelines

- **Style**: Fashion editorial — curated, magazine-cover quality
- **Color treatment**: Muted palette, Kodachrome film look
- **Corner radius**: 6pt
- **Subjects**: Landscapes or people, fashion editorial style, consistently beautiful
- **Avoid**: Oversaturated/neon colors, amateur-looking shots, inconsistent visual tone
- **AI prompt prefix**: `editorial photography, desaturated Kodachrome palette, cinematic composition, magazine-cover quality, muted tones, film grain, emotionally evocative`

### Chart Guidelines

- **Primary palette**: Brown sand (#B78A66), teal (#00D2E0), sun red (#FF375F), then semantic colors
- **Sequential**: Light-to-dark brown sand gradient (7 stops)
- **Diverging**: Sun red ↔ Teal through neutral (#F5F5F7)
- **Highlight color**: #FF375F (sun red) on #FFFFFF contrast
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
