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
license: MIT
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

### Imagery Guidelines

- **Style**: Artistic black and white — inspired by Peter Lindbergh and Ellen von Unwerth
- **Color treatment**: Black and white exclusively
- **Corner radius**: 4pt
- **Subjects**: Surf culture, shapers, young entrepreneurs, top-model-class beauty
- **Avoid**: Color photography, corporate imagery, generic stock photos
- **AI prompt prefix**: `high-contrast black and white photography in the style of Peter Lindbergh and Ellen von Unwerth, dramatic lighting, editorial fashion composition, breathtaking beauty, raw emotion, film grain, unretouched natural skin, soulful portraits`
- **Grounding references**: Peter Lindbergh, Ellen von Unwerth (use with `enable_web_search: true`)

### Chart Guidelines

- **Palette**: Gray-only — no color in charts, matching the brand's monochrome identity
- **Sequential**: Light-to-dark gray (7 stops from #F5F5F7 to #48484A)
- **Diverging**: Symmetric gray gradient through white center
- **Highlight color**: #1C1C1E (near-black) on #FFFFFF contrast
- **Figure background**: #F5F5F7 (matches page background), plot area #FFFFFF
- Charts use brand typography tokens (h3 for titles, body-sm for axis labels, caption for ticks/legends)

## Usage with PDF Factory

1. Pass this skill's directory path as `--brand` to render.py and compose.py
2. Scripts read `assets/manifest.json` for fonts, logos, templates, and tokens
3. The `manifest.json["tokens"]` section drives all styling — colors and type scale
4. Zone overlays on covers/dividers use tokens for font, size, color, and alignment
5. SVG logos from `assets/logos/` are rendered as vectors on cover pages
6. Content pages are styled via dynamically generated CSS from the same tokens

Keep `manifest.json["tokens"]` in sync with `references/tokens.md`.
