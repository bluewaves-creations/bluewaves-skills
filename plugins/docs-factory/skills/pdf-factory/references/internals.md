# PDF Factory Internals

Read when debugging rendering issues or understanding pipeline behavior.

## Font Registration

The pipeline registers fonts at two levels:

1. **xhtml2pdf** (render.py) — Generates `@font-face` CSS declarations with absolute
   paths to TTF files. Font families use `Brand-{role}` names (e.g., `Brand-body`,
   `Brand-heading`, `Brand-mono`). xhtml2pdf resolves these via its own CSS engine.
   **Do not** use reportlab `TTFont()` names directly in CSS — xhtml2pdf ignores them.

2. **reportlab** (compose.py) — Registers `TTFont("Brand-{role}-{variant}", path)`
   and `addMapping()` for bold/italic. Used by zone overlays on cover/divider pages.

## Zone Overlays

Zone text on covers and dividers is rendered by compose.py using reportlab canvas,
NOT xhtml2pdf. Each zone in `zones.json` specifies:
- `style` → looks up `manifest.tokens.type_scale[style]` for size_pt, weight, font role
- `color_role` → looks up `manifest.tokens.colors[color_role]` for hex color
- `align` → left, center, or right
- `type: "image"` → renders SVG logo via svglib

Text auto-shrinks if it overflows the zone width.

## Section Page Breaks

render.py preprocesses the HTML via `_insert_section_breaks()`, which injects
`<div style="page-break-before: always;"></div>` before every `<h1>` except
the first. This is an HTML-level transformation, not a CSS rule. Do NOT add
`page-break-before` to h1 in base.css — that creates a blank first page.

When `--sections` is passed to render.py, h1 headings that match a section title
are replaced with invisible text markers (1pt white text). This prevents the title
from appearing on both the section divider page and the content page. The invisible
text is still detected by compose.py's pypdf text extraction, so section detection
continues to work. Section titles must exactly match the H1 text in the HTML.

compose.py auto-detects section boundaries by scanning the rendered content pages for
text matching the section titles in metadata.json. This means the `page` values in
metadata sections are only hints — compose.py will find the correct pages from the
rendered output. You still need section titles in metadata.json to be accurate.

## Orphan Title Prevention

base.css applies `-pdf-keep-with-next: true` to all headings (h1–h4). This is an
xhtml2pdf-specific property. The standard `page-break-after: avoid` is parsed
but NOT enforced by xhtml2pdf — do not use it.

## SVG Rendering

render.py preprocesses HTML to convert SVG content to high-DPI PNG before
xhtml2pdf rendering:
- `<img src="*.svg">` references → svglib conversion at 300 DPI
- Inline `<svg>` blocks → extracted, converted, replaced with `<img>` tags
- Uses svglib + reportlab `renderPM` (no new dependencies)
- Graceful fallback: on failure, original tag is preserved

## Image Corner Radius

Brand kits define `tokens.imagery.corner_radius_pt`:
- **Decathlon**: 0pt (no rounding)
- **Bluewaves**: 6pt
- **Wave Artisans**: 4pt

render.py applies Pillow-based rounded corners to all raster images when
`corner_radius_pt > 0`. Radius is converted from pt to pixels at output DPI.
SVGs and data URIs are excluded.

## Chart Integration

Charts from the `chart-designer` skill embed as standard images. Use `<figure>`
and `<figcaption>` for captioned charts:

```html
<figure>
  <img src="chart.png" alt="Chart title">
  <figcaption>Figure 1: Description</figcaption>
</figure>
```

## Image Generation

When generating images for a document, read the brand kit's `tokens.imagery`
for creative direction and `tokens.imagery.pdf_defaults` for technical settings:

| Token | Purpose |
|-------|---------|
| `prompt_style` | Append to image prompts for brand-consistent style |
| `color_treatment` | Color/B&W guidance |
| `pdf_defaults.resolution` | Resolution to request (typically `"2K"`) |
| `pdf_defaults.output_format` | Format to request (typically `"jpeg"`) |
| `pdf_defaults.enable_web_search` | Whether to enable web search grounding |

Apply these settings when calling the image generation skill. The `subject_guidelines`
and `avoid` arrays provide editorial direction for prompt crafting.

## CSS Specifics

Heading spacing (margin-bottom): h1 16pt, h2 12pt, h3 8pt, h4 6pt.
List indentation: `padding-left: 14pt` on ul/ol.
Code/table background: `#F0F0F0` (base.css structural default, overridden by
brand token `background-alt` if different).

## Token Resolution

Scripts read tokens from `manifest.json["tokens"]`, not from `references/tokens.md`.
The `references/tokens.md` file is for Claude to understand the design system;
the `manifest.json["tokens"]` section is the machine-readable source for scripts.
Both must stay in sync.
