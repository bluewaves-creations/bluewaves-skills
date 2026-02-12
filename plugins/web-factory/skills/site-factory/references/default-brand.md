# Default Brand — Bluewaves Neutral

Built-in neutral brand for site-factory. Uses a gray palette inspired by wave-artisans, the Bluewaves logo, and system fonts. Zero external dependencies — works in standalone ZIP mode.

## Colors

| Token | Value | Usage |
|---|---|---|
| `text-heading` | `#1C1C1E` | Headings |
| `text-body` | `#1C1C1E` | Body text |
| `text-muted` | `#8E8E93` | Captions, footer |
| `text-inverse` | `#FFFFFF` | Text on dark bg |
| `background-page` | `#F5F5F7` | Page bg |
| `background-alt` | `#FFFFFF` | Code blocks, cards |
| `border-default` | `#C7C7CC` | Borders |
| `border-strong` | `#48484A` | Strong borders |
| `link` | `#0091FF` | Links |
| `highlight` | `#6B5DFF` | Accents, blockquotes |

## Typography

System font stacks — no custom font files required.

| Role | Font stack |
|---|---|
| Body / Heading | `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif` |
| Code | `ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace` |

## Type Scale

| Level | Size |
|---|---|
| H1 | 40px |
| H2 | 32px |
| H3 | 25px |
| H4 | 20px |
| Body | 16px |
| Small | 14px |
| Code | 15px |

## Logo

Path: `assets/default-logo.svg`

Copy to `build/assets/images/logo.svg` during build.

## Usage

The default brand values are baked into `skeleton.html`'s `:root` block. When using the default brand:

1. No `@font-face` blocks needed — system fonts are already declared
2. No fonts directory needed in `build/assets/`
3. Just fill the content placeholders (`{{TITLE}}`, `{{BRAND_NAME}}`, etc.) and copy the logo
