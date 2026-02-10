# docs-factory Plugin

Branded document generation with three brand kits, a chart designer for data visualizations, and a PDF rendering engine for production-grade typeset output from markdown.

## Installation

```bash
# Add the Bluewaves marketplace
/plugin marketplace add bluewaves-creations/bluewaves-skills

# Install this plugin
/plugin install docs-factory@bluewaves-skills
```

## Prerequisites

**Python Version**: Requires Python 3.8 or higher

```bash
# Install all required packages (run the command or use the slash command)
/docs-factory:install-deps

# Or manually with pip
pip install xhtml2pdf reportlab pypdf pyhanko markdown lxml pillow html5lib cssselect2
pip install matplotlib numpy
```

## Skills Included

| Skill | Description |
|-------|-------------|
| **brand-bluewaves** | Brand kit for Bluewaves — Merriweather typography, brown sand primary, teal/red accents |
| **brand-wave-artisans** | Brand kit for Wave Artisans — Nunito Sans typography, gray-driven minimalist palette |
| **brand-decathlon** | Brand kit for Decathlon — Inter typography, blue/purple primary, green accent |
| **chart-designer** | Brand-consistent charts and data visualizations using matplotlib — 10 chart types with automatic brand kit integration |
| **pdf-factory** | PDF rendering engine — converts markdown to professionally typeset PDF using brand kits |

## Usage Examples

### Generate a branded PDF
> "Generate a PDF report for Bluewaves from this markdown"

### Use a specific brand
> "Create a Decathlon-branded proposal from proposal.md"

### Quick PDF from markdown
> "Convert this markdown file to a professional PDF"

## Slash Commands

| Command | Description |
|---------|-------------|
| `/docs-factory:install-deps` | Install Python dependencies for PDF rendering |
| `/docs-factory:generate-pdf` | Full-workflow PDF generation from markdown |

## How It Works

1. **Brand kits** provide design tokens (colors, typography, spacing), font files, logo variants, PDF page templates with content zones, and decorative patterns
2. **pdf-factory** consumes a brand kit and markdown content to produce professional PDFs through a 6-step pipeline: resolve brand → parse markdown → render content → compose document → validate → sign (optional)

## Brand Kits

### Bluewaves (Merriweather)
- Primary: brown sand (#B78A66)
- Accents: teal ocean (#00D2E0), sun red (#FF375F)
- Typography: Merriweather for headings and body

### Wave Artisans (Nunito Sans)
- Gray-driven palette with subtle light gray backgrounds
- Typography: Nunito Sans for headings and body

### Decathlon (Inter)
- Primary: blue/purple (#3643BA)
- Accent: green (#7AFFA6) on blue backgrounds only
- Typography: Inter for headings and body

## Placeholder Assets

Brand kits include placeholder font, logo, template, and pattern files. Replace placeholder files in `assets/` with actual brand assets before production use.

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "Missing Python packages" | Run `/docs-factory:install-deps` |
| "Font not embedded" | Verify font path in manifest matches actual file in assets/fonts/ |
| "Page count 0" | Verify render.py produced output; check input HTML is not empty |
| "Brand font missing" | Confirm all fonts declared in manifest exist on disk |

### Verifying Your Setup

```bash
# Check Python version (requires 3.8+)
python3 --version

# Verify all packages are installed
python3 -c "import xhtml2pdf, reportlab, pypdf, markdown, lxml, PIL, html5lib, cssselect2; print('All packages OK')"
```

## License

MIT
