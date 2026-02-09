# Wave Artisans Design Tokens

## Colors

### Brand Colors

Gray-driven palette — no single primary color. The gray itself is the identity.

| Role | Name | Hex | RGB |
|------|------|-----|-----|
| Background | Light Gray | #F5F5F7 | 245, 245, 247 |
| Text | Near Black | #1C1C1E | 28, 28, 30 |

Semantic colors used as-needed for accent and categorization. No dedicated primary or accent.

### Neutral Colors

| Token | Hex | RGB |
|-------|-----|-----|
| neutral-900 | #1C1C1E | 28, 28, 30 |
| neutral-700 | #48484A | 72, 72, 74 |
| neutral-500 | #8E8E93 | 142, 142, 147 |
| neutral-300 | #C7C7CC | 199, 199, 204 |
| neutral-100 | #F5F5F7 | 245, 245, 247 |
| white | #FFFFFF | 255, 255, 255 |

Never use pure black (#000000) for text. Body text is neutral-900 (#1C1C1E).

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
| text-heading | neutral-900 (#1C1C1E) |
| text-body | neutral-900 (#1C1C1E) |
| text-muted | neutral-500 (#8E8E93) |
| text-inverse | white (#FFFFFF) |
| background-page | neutral-100 (#F5F5F7) |
| background-alt | white (#FFFFFF) |
| background-dark | neutral-900 (#1C1C1E) |
| border-default | neutral-300 (#C7C7CC) |
| border-strong | neutral-700 (#48484A) |
| link | Blue (#0091FF) |
| highlight | Indigo (#6B5DFF) |

## Typography

### Fonts

| Role | Family | Files |
|------|--------|-------|
| Heading | Nunito Sans | heading.ttf, heading-bold.ttf |
| Body | Nunito Sans | body.ttf, body-italic.ttf, body-bold.ttf, body-bold-italic.ttf |
| Mono | Fira Code | mono.ttf |

### Type Scale

| Token | Size (pt) | Size (px) | Weight | Font | Line Height | Letter Spacing |
|-------|-----------|-----------|--------|------|-------------|----------------|
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
