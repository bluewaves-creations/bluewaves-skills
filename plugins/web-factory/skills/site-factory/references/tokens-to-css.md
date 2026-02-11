# Brand Tokens → CSS Custom Properties

Mapping table for converting `manifest.json` brand tokens to CSS custom properties used in `skeleton.html`.

## Color Tokens

| manifest.json path | CSS custom property | Usage |
|---|---|---|
| `tokens.colors.text-heading` | `--color-heading` | h1-h4 headings, header text |
| `tokens.colors.text-body` | `--color-body` | Body text, paragraphs, lists |
| `tokens.colors.text-muted` | `--color-muted` | Captions, TOC headers, footer |
| `tokens.colors.text-inverse` | `--color-inverse` | Text on dark backgrounds |
| `tokens.colors.background-page` | `--bg-page` | Page background |
| `tokens.colors.background-alt` | `--bg-alt` | Code blocks, table headers, blockquotes |
| `tokens.colors.border-default` | `--border` | Borders, dividers, table cells |
| `tokens.colors.border-strong` | `--border-strong` | Emphasized borders |
| `tokens.colors.link` | `--color-link` | Anchor tags, TOC links, attachment links |
| `tokens.colors.highlight` | `--color-highlight` | Accent color, buttons, blockquote border |

## Typography Tokens

Convert point sizes to pixels: **multiply by 1.333** (CSS standard pt→px ratio).

| manifest.json path | CSS custom property | Conversion |
|---|---|---|
| `tokens.type_scale.h1.size_pt` | `--font-size-h1` | `32pt × 1.333 = 43px` |
| `tokens.type_scale.h2.size_pt` | `--font-size-h2` | `24pt × 1.333 = 32px` |
| `tokens.type_scale.h3.size_pt` | `--font-size-h3` | `18pt × 1.333 = 24px` |
| `tokens.type_scale.h4.size_pt` | `--font-size-h4` | `14pt × 1.333 = 19px` |
| `tokens.type_scale.body.size_pt` | `--font-size-body` | `11pt × 1.333 = 15px` |
| `tokens.type_scale.body-sm.size_pt` | `--font-size-small` | `9pt × 1.333 = 12px` |
| `tokens.type_scale.code.size_pt` | `--font-size-code` | `10pt × 1.333 = 13px` |

## Font Tokens

Map font file paths from the manifest to `@font-face` declarations.

| manifest.json path | CSS font-family | Weight/Style | Usage |
|---|---|---|---|
| `fonts.heading.bold` | `Brand-Heading` | `700` | h1-h4, nav headers, aside headers |
| `fonts.body.regular` | `Brand-Body` | `400` | Body text, paragraphs |
| `fonts.body.bold` | `Brand-Body` | `700` | Bold text within body |
| `fonts.body.italic` | `Brand-Body` | `400 italic` | Italic text within body |
| `fonts.body.bold_italic` | `Brand-Body` | `700 italic` | Bold italic text |
| `fonts.mono.regular` | `Brand-Mono` | `400` | Code blocks, inline code |

Font files are copied to `build/assets/fonts/` and referenced with relative URLs.

## Imagery Tokens

| manifest.json path | CSS custom property | Usage |
|---|---|---|
| `tokens.imagery.corner_radius_pt` | `--border-radius` | Convert pt→px (×1.333). Applied to images, code blocks, cards |

## Logo

Use `logos.full.color` for the header logo. Copy the SVG to `build/assets/images/logo.svg`.

## Example

For the Bluewaves brand kit:

```css
:root {
  --color-heading: #B78A66;
  --color-body: #2C2C2C;
  --color-muted: #7A7A7A;
  --color-inverse: #FFFFFF;
  --bg-page: #FFFFFF;
  --bg-alt: #F5F5F7;
  --border: #B0B0B0;
  --border-strong: #4A4A4A;
  --color-link: #00D2E0;
  --color-highlight: #FF375F;

  --font-size-h1: 43px;
  --font-size-h2: 32px;
  --font-size-h3: 24px;
  --font-size-h4: 19px;
  --font-size-body: 15px;
  --font-size-small: 12px;
  --font-size-code: 13px;

  --border-radius: 8px;
}
```
