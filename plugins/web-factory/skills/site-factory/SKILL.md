---
name: site-factory
description: Build single-page branded websites from markdown content with optional docs-factory brand kit. Use when the user wants to create a website, web page, or HTML site from markdown.
allowed-tools: Bash, Read, Write
license: MIT
compatibility: Python 3.8+ (stdlib only for site_api.py)
---
# Site Factory

Build single-page websites from markdown content. Works out of the box with a neutral default brand, or optionally use a docs-factory brand kit for custom styling.

## Workflow

### Step 0: Choose Brand Slug

Ask the user for a **brand slug** (subdomain) and **site name** (URL path).

1. **Suggest options** based on context — e.g. `bluewaves`, `mycompany`, or something relevant to the content
2. **Validate slug format**: must match `^[a-z0-9]([a-z0-9-]*[a-z0-9])?$`, 1–63 characters
3. **Validate site name format**: lowercase letters, numbers, and hyphens only
4. **Check availability**:
   ```bash
   python3 scripts/site_api.py info {brand} {site-name}
   ```
   A 404 response means the name is available. Any other response means it's taken.
5. **Confirm** the chosen slug and site name with the user before proceeding

### Step 1: Resolve Brand Kit (Optional)

By default, use the **built-in neutral brand** — skip directly to Step 3. The default brand uses a gray palette, system fonts, and the Bluewaves logo. See `references/default-brand.md` for details.

If the user explicitly requests a docs-factory brand kit, read its `assets/manifest.json`:

```bash
cat plugins/docs-factory/skills/brand-{BRAND}/assets/manifest.json
```

Available brand kits:
- `brand-bluewaves` — Merriweather typography, brown sand primary (#B78A66)
- `brand-wave-artisans` — Nunito Sans typography, gray minimalist palette
- `brand-decathlon` — Inter typography, blue/purple primary (#3643BA)

### Step 2: Map Design Tokens to CSS (Brand Kit Only)

**Skip this step when using the default brand** — values are already baked into `skeleton.html`.

When using a docs-factory brand kit, use `references/tokens-to-css.md` to map `manifest.json` tokens to CSS custom properties. Key mappings:

| Token path | CSS property | Example |
|---|---|---|
| `tokens.colors.text-heading` | `--color-heading` | `#B78A66` |
| `tokens.colors.background-page` | `--bg-page` | `#FFFFFF` |
| `tokens.colors.highlight` | `--color-highlight` | `#FF375F` |
| `tokens.type_scale.h1.size_pt` | `--font-size-h1` | `43px` (32pt x 1.333) |
| `fonts.heading.bold` | `@font-face Brand-Heading` | `fonts/heading-bold.ttf` |

### Step 3: Generate HTML

Using `references/skeleton.html` as the template:

**Default brand:**
- The `:root` block already contains hardcoded default values — no CSS overrides needed
- Just fill the content placeholders: `{{TITLE}}`, `{{BRAND_NAME}}`, `{{TOC_ITEMS}}`, `{{CONTENT}}`, `{{ATTACHMENT_ITEMS}}`, `{{DATE}}` — `{{TITLE}}` is right-aligned in the header
- Copy `assets/default-logo.svg` to `build/assets/images/logo.svg`

**Brand kit override:**
- Replace the entire `:root` block with brand-specific CSS custom property values
- Add `@font-face` blocks for the brand's custom fonts (heading, body, mono)
- Update `font-family` declarations to reference `"Brand-Heading"`, `"Brand-Body"`, `"Brand-Mono"` with system font fallbacks
- Copy the brand logo SVG to `build/assets/images/logo.svg`

Content structure (same for both paths):
1. **Header**: Logo (left) + document title (right)
2. **Navigation**: Auto-generated TOC from H2/H3 headings in the markdown
3. **Main content**: Convert markdown to HTML — use semantic tags (`<h2>`, `<p>`, `<ul>`, `<table>`, `<pre><code>`, `<blockquote>`)
4. **Attachments sidebar**: Download links for any attached files (PDFs, images, data files)
5. **Footer**: Small logo + brand name + current date

### Step 4: Build Output Directory

Create a `build/` directory with this structure:

**Default brand:**
```
build/
├── index.html          # Generated HTML with inline CSS
├── assets/
│   └── images/         # Content images + default-logo.svg as logo.svg
└── files/              # Downloadable attachments (PDFs, data files)
```

No `fonts/` directory is needed — the default brand uses system fonts.

**Brand kit:**
```
build/
├── index.html          # Generated HTML with brand CSS overrides
├── assets/
│   ├── images/         # Content images + brand logo as logo.svg
│   └── fonts/          # Brand fonts (.ttf files from manifest)
└── files/              # Downloadable attachments (PDFs, data files)
```

Copy assets:
- **Logo**: Default → `assets/default-logo.svg`; Brand kit → brand logo SVG from manifest
- **Fonts** (brand kit only): Copy from brand kit `assets/fonts/` to `build/assets/fonts/`
- **Images**: Copy content images to `build/assets/images/`
- **Attachments**: Copy any attached files to `build/files/`

### Step 5: Verify

Check the build directory:
- `index.html` exists and is valid HTML5
- All referenced images and files are present
- **Default brand**: No `@font-face` blocks, system fonts used, no `build/assets/fonts/` directory
- **Brand kit**: CSS custom properties populated with brand values, all referenced fonts present
- TOC links match heading IDs
- Responsive layout works (check `@media` queries in CSS)

Report the build directory contents and total size.

## Output

The `build/` directory is ready for publishing with site-publisher:

```bash
# Default brand (no --brand-kit flag)
python3 scripts/site_api.py publish ./build {brand} {site-name} --title "Document Title"

# With brand kit (optional)
python3 scripts/site_api.py publish ./build {brand} {site-name} --title "Document Title" --brand-kit path/to/manifest.json
```

## Notes

- The default brand requires zero external dependencies — works in standalone ZIP mode
- When using a brand kit, all font files must be copied locally (no CDN references) for offline support
- Images should be optimized before inclusion (reasonable file sizes)
- The HTML is a single page with anchor-based navigation via TOC
- CSS custom properties enable the login page to share brand colors
