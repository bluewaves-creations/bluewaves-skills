# Decathlon Design Tokens

## Colors

### Brand Colors

| Role | Name | Hex | RGB |
|------|------|-----|-----|
| Primary | Blue/Purple | #3643BA | 54, 67, 186 |
| Accent | Green | #7AFFA6 | 122, 255, 166 |

Accent green is only used on blue/dark backgrounds. No rounded corners.

### Neutral Colors

| Token | Hex | RGB |
|-------|-----|-----|
| neutral-900 | #212121 | 33, 33, 33 |
| neutral-700 | #4A4A4A | 74, 74, 74 |
| neutral-500 | #7A7A7A | 122, 122, 122 |
| neutral-300 | #B0B0B0 | 176, 176, 176 |
| neutral-100 | #F0F0F0 | 240, 240, 240 |
| white | #FFFFFF | 255, 255, 255 |

Never use pure black (#000000) for text. Body text is neutral-900 (#212121).

### Shared Semantic Colors

Used for status, feedback, and categorization across all brands.

| Name | Hex | RGB |
|------|-----|-----|
| Red | #FF4245 | 255, 66, 69 |
| Orange | #FF9230 | 255, 146, 48 |
| Yellow | #FFD600 | 255, 214, 0 |
| Green | #30D158 | 48, 209, 88 |
| Mint | #00DAC3 | 0, 218, 195 |
| Teal | #00D2E0 | 0, 210, 224 |
| Cyan | #3CD3FE | 60, 211, 254 |
| Blue | #0091FF | 0, 145, 255 |
| Indigo | #6B5DFF | 107, 93, 255 |
| Purple | #DB34F2 | 219, 52, 242 |
| Pink | #FF375F | 255, 55, 95 |
| Brown | #B78A66 | 183, 138, 102 |

### Color Roles

| Role | Maps to |
|------|---------|
| text-heading | primary (#3643BA) |
| text-body | neutral-900 (#212121) |
| text-muted | neutral-500 (#7A7A7A) |
| text-inverse | white (#FFFFFF) |
| background-page | white (#FFFFFF) |
| background-alt | neutral-100 (#F0F0F0) |
| background-dark | primary (#3643BA) |
| border-default | neutral-300 (#B0B0B0) |
| border-strong | neutral-700 (#4A4A4A) |
| link | primary (#3643BA) |
| highlight | accent (#7AFFA6) |

## Typography

### Fonts

| Role | Family | Files |
|------|--------|-------|
| Heading | Inter | heading.ttf, heading-bold.ttf |
| Body | Inter | body.ttf, body-italic.ttf, body-bold.ttf, body-bold-italic.ttf |
| Mono | Fira Code | mono.ttf |

### Type Scale

| Token | Size (pt) | Size (px) | Weight | Font | Line Height | Letter Spacing |
|-------|-----------|-----------|--------|------|-------------|----------------|
| display-lg | 72 | 96 | bold | heading | 1.0 | -0.02em |
| display | 48 | 64 | bold | heading | 1.1 | -0.02em |
| h1 | 32 | 42 | bold | heading | 1.15 | -0.01em |
| h2 | 24 | 32 | bold | heading | 1.2 | 0 |
| h3 | 18 | 24 | bold | heading | 1.25 | 0 |
| h4 | 14 | 18 | bold | heading | 1.3 | 0 |
| body | 11 | 16 | regular | body | 1.5 | 0 |
| body-sm | 9 | 14 | regular | body | 1.5 | 0 |
| caption | 8 | 12 | regular | body | 1.4 | 0.01em |
| overline | 8 | 11 | bold | body | 1.4 | 0.08em (uppercase) |
| code | 10 | 14 | regular | mono | 1.5 | 0 |

### Paragraph Settings

- Max width: 75 characters
- Spacing after: 6pt
- First line indent: none

### Special Rules

- No rounded corners on any element
- Accent green (#7AFFA6) only appears on primary blue or dark backgrounds

## Spacing

### Base Unit

6pt

### Scale

| Token | Value (pt) |
|-------|-----------|
| xs | 6 |
| sm | 12 |
| md | 18 |
| lg | 24 |
| xl | 36 |
| 2xl | 48 |
| 3xl | 72 |

### Page Geometry

| Property | Value |
|----------|-------|
| Format | A4 |
| Width | 210mm |
| Height | 297mm |
| Margin top | 25mm |
| Margin bottom | 25mm |
| Margin left | 25mm |
| Margin right | 25mm |
| Bleed | 3mm |

### Grid

- Columns: 12
- Gutter: 12pt
- Content width: 453pt

## Shadows

| Token | Value |
|-------|-------|
| none | none |
| sm | 0 1px 2px rgba(0,0,0,0.05) |
| md | 0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06) |
| lg | 0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05) |
| xl | 0 20px 25px rgba(0,0,0,0.1), 0 10px 10px rgba(0,0,0,0.04) |
