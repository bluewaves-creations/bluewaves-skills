---
name: site-factory
description: >
  Build branded single-page websites from markdown content using docs-factory
  brand kits. Reads brand kit manifest.json, maps design tokens to CSS custom
  properties, generates responsive HTML with header, TOC, content, attachments,
  and footer. Outputs a build/ directory ready for site-publisher. This skill
  should be used when the user wants to create a branded website, web page,
  or HTML site from markdown content. Triggers on requests mentioning website
  creation, branded web pages, HTML generation from markdown, or web publishing.
allowed-tools: Bash, Read, Write
license: MIT
compatibility: Python 3.8+ (stdlib only for site_api.py)
---
# Site Factory

Build branded single-page websites from markdown content using docs-factory brand kits.

## Workflow

### Step 1: Resolve Brand Kit

Read the brand kit's `assets/manifest.json` from docs-factory. Available brands:
- `brand-bluewaves` — Merriweather typography, brown sand primary (#B78A66)
- `brand-wave-artisans` — Nunito Sans typography, gray minimalist palette
- `brand-decathlon` — Inter typography, blue/purple primary (#3643BA)

```bash
cat plugins/docs-factory/skills/brand-{BRAND}/assets/manifest.json
```

### Step 2: Map Design Tokens to CSS

Use `references/tokens-to-css.md` to map `manifest.json` tokens to CSS custom properties. Key mappings:

| Token path | CSS property | Example |
|---|---|---|
| `tokens.colors.text-heading` | `--color-heading` | `#B78A66` |
| `tokens.colors.background-page` | `--bg-page` | `#FFFFFF` |
| `tokens.colors.highlight` | `--color-highlight` | `#FF375F` |
| `tokens.type_scale.h1.size_pt` | `--font-size-h1` | `43px` (32pt x 1.333) |
| `fonts.heading.bold` | `@font-face Brand-Heading` | `fonts/heading-bold.ttf` |

### Step 3: Generate HTML

Using `references/skeleton.html` as the template:

1. **Header**: Brand logo (from `logos.full.color`) + document title
2. **Navigation**: Auto-generated TOC from H2/H3 headings in the markdown
3. **Main content**: Convert markdown to HTML directly — use semantic tags (`<h2>`, `<p>`, `<ul>`, `<table>`, `<pre><code>`, `<blockquote>`)
4. **Attachments sidebar**: Download links for any attached files (PDFs, images, data files)
5. **Footer**: Brand name + current date

### Step 4: Build Output Directory

Create a `build/` directory with this structure:

```
build/
├── index.html          # Generated HTML with inline CSS custom properties
├── style.css           # Base stylesheet (from skeleton.html's <style>)
├── assets/
│   ├── images/         # Content images from markdown
│   └── fonts/          # Brand fonts (.ttf files from manifest)
└── files/              # Downloadable attachments (PDFs, data files)
```

Copy assets:
- **Fonts**: Copy from brand kit `assets/fonts/` to `build/assets/fonts/`
- **Images**: Copy content images to `build/assets/images/`
- **Logos**: Copy brand logo SVG to `build/assets/images/`
- **Attachments**: Copy any attached files to `build/files/`

### Step 5: Verify

Check the build directory:
- `index.html` exists and is valid HTML5
- All referenced fonts, images, and files are present
- CSS custom properties are populated with brand values
- TOC links match heading IDs
- Responsive layout works (check `@media` queries in CSS)

Report the build directory contents and total size.

## Output

The `build/` directory is ready for publishing with site-publisher:

```bash
python3 scripts/site_api.py publish ./build {brand} {site-name} --title "Document Title" --brand-kit path/to/manifest.json
```

## Notes

- All font files must be copied locally (no CDN references) for offline support
- Images should be optimized before inclusion (reasonable file sizes)
- The HTML is a single page with anchor-based navigation via TOC
- CSS custom properties enable the login page to share brand colors
