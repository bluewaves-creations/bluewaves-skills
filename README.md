# Bluewaves Skills

![Bluewaves — We craft AI products you can actually use](bluewaves.png)

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A Claude Code plugin marketplace featuring Athena document exchange, branded document generation with charts, EPUB creation, and skill creation and cross-platform conversion tools.

> **Looking for media-factory or web-factory?** Those plugins moved to [bluewaves-skills-rooms](https://github.com/bluewaves-creations/bluewaves-skills-rooms).

## Installation

Add this marketplace to Claude Code:

```bash
/plugin marketplace add bluewaves-creations/bluewaves-skills
```

## Available Plugins

### epub-generator

Production-grade EPUB 3 generation with validation, nested TOC, and dependency checking.

```bash
/plugin install epub-generator@bluewaves-skills
```

**Skills:**
- `epub-creator` - Convert markdown files to EPUB with cover, nested TOC, and styling

**Features:**
- Pre-validation of source files before processing
- Post-validation with comprehensive EPUB checks
- Hierarchical table of contents (H1/H2/H3)
- Progress reporting during generation
- Automatic dependency validation hook

**Prerequisites:** `pip install ebooklib markdown Pillow beautifulsoup4 lxml PyYAML`

---

### athena

Bidirectional document exchange with the Athena note-taking app. Process `.athenabrief` research packages and create `.athena` import packages.

```bash
/plugin install athena@bluewaves-skills
```

**2 Skills:**

| Category | Skills |
|----------|--------|
| **Processing** | `athena-work` |
| **Packaging** | `athena-package` |

- **athena-work** - Process `.athenabrief` research packages with progressive disclosure, zero-instruction support, and automatic result packaging
- **athena-package** - Create validated `.athena` import packages with manifest, markdown notes, aurora tags, and optional assets

**Prerequisites:** Python 3.8+ (stdlib only, no additional packages)

---

### docs-factory

Branded document generation with three brand kits, a chart designer, and a PDF rendering engine.

```bash
/plugin install docs-factory@bluewaves-skills
```

**5 Skills:**

| Category | Skills |
|----------|--------|
| **Brand Kits** | `brand-bluewaves`, `brand-wave-artisans`, `brand-decathlon` |
| **Charts** | `chart-designer` |
| **PDF Engine** | `pdf-factory` |

- **brand-bluewaves** - Merriweather typography, brown sand primary, teal/red accents, imagery + chart tokens
- **brand-wave-artisans** - Nunito Sans typography, gray-driven minimalist palette, B&W imagery + gray charts
- **brand-decathlon** - Inter typography, blue/purple primary, green accent, imagery + chart tokens
- **chart-designer** - Brand-consistent chart design system for matplotlib (load_theme, apply, named sizes)
- **pdf-factory** - Production-grade PDF rendering from markdown with SVG support and image corner radius

**Prerequisites:** Python 3.8+ with `pip install xhtml2pdf reportlab pypdf pyhanko markdown lxml pillow html5lib cssselect2 matplotlib numpy`

---

### skills-factory

Skill creation, validation, and cross-platform conversion tools for Agent Skills.

```bash
/plugin install skills-factory@bluewaves-skills
```

**3 Skills:**

| Category | Skills |
|----------|--------|
| **Skill Creation** | `skill-shaper` |
| **Cross-Platform Conversion** | `gemini-gem-converter`, `openai-gpt-converter` |

- **skill-shaper** - Create effective Agent Skills with guided workflows, bundled scripts, and reference materials
- **gemini-gem-converter** - Convert Agent Skills to Gemini Gems with platform constraint awareness
- **openai-gpt-converter** - Convert Agent Skills to Custom GPTs with 8K instruction limit strategies

**Prerequisites:** `skills-ref` recommended for validation (`uv pip install -e deps/agentskills/skills-ref/`). Fallback: PyYAML for `quick_validate.py`.

---

## Slash Commands

Explicit commands you can invoke from the Claude Code prompt. These complement skills (which trigger automatically).

### Project-Level

| Command | Description |
|---------|-------------|
| `/validate-skills` | Validate marketplace skills via skills-ref |
| `/build-skill-zips` | Build standalone skill ZIP files for Claude.ai users |

### epub-generator

| Command | Description |
|---------|-------------|
| `/epub-generator:install-deps` | Install Python dependencies (uses `uv` by default, `--pip` for pip) |

### athena

| Command | Description |
|---------|-------------|
| `/athena:inspect-package <path>` | Inspect contents of a `.athenabrief` or `.athena` package |
| `/athena:validate-package <path>` | Validate a `.athena` package against the import spec |

### docs-factory

| Command | Description |
|---------|-------------|
| `/docs-factory:install-deps` | Install Python dependencies for PDF rendering |
| `/docs-factory:generate-pdf <file> [--brand <name>]` | Generate a branded PDF from markdown |

### skills-factory

| Command | Description |
|---------|-------------|
| `/skills-factory:init-skill <name> --path <dir>` | Scaffold a new skill from template |
| `/skills-factory:validate-skill <path>` | Validate a skill folder |
| `/skills-factory:package-skill <path> [output-dir]` | Package a skill into a `.skill` ZIP |

---

## Use Without Claude Code

Individual skills are available as standalone ZIP files for **Claude.ai** (web/desktop) users who don't use Claude Code.

### How to install a skill in Claude.ai

1. Download the `.zip` file for the skill you want from the [latest GitHub release](https://github.com/bluewaves-creations/bluewaves-skills/releases)
2. In Claude.ai, go to **Settings > Capabilities**
3. Click **Upload skill** and select the downloaded ZIP
4. Toggle the skill **ON**

Each ZIP contains a single skill with its instructions. All 11 skills are available individually.

> **Note:** Plugin hooks (dependency checks) are Claude Code-only features and won't apply when using skills directly in Claude.ai.

---

## Usage Examples

```
# Generate EPUB
"Create an EPUB from the markdown files in ./chapters"

# Process Athena research brief
"Summarize the key findings from this athenabrief"
"Process this research package and create action items"

# Create Athena notes
"Package these meeting notes for Athena"
"Turn this conversation into Athena notes"

# Generate branded PDF with charts
"Generate a PDF report for Bluewaves from this markdown"
"Create a Decathlon-branded proposal with revenue charts"

# Create a chart
"Create a bar chart of quarterly revenue using the Decathlon brand"

# Create a skill
"Help me create a skill for processing CSV files"

# Convert a skill to other platforms
"Convert my pdf-processor skill to a Gemini Gem"
"Adapt this skill for use as a Custom GPT"
```

## Updating

To get the latest skills and updates:

```bash
/plugin marketplace update bluewaves-skills
```

This pulls the latest changes from the repository.

## Uninstalling

Remove a plugin:
```bash
/plugin uninstall epub-generator@bluewaves-skills
```

Remove the marketplace entirely:
```bash
/plugin marketplace remove bluewaves-skills
```

## Team Distribution

Add to your project's `.claude/settings.json` for automatic marketplace loading:

```json
{
  "extraKnownMarketplaces": {
    "bluewaves-skills": {
      "source": {
        "source": "github",
        "repo": "bluewaves-creations/bluewaves-skills"
      }
    }
  },
  "enabledPlugins": {
    "epub-generator@bluewaves-skills": true,
    "athena@bluewaves-skills": true,
    "skills-factory@bluewaves-skills": true,
    "docs-factory@bluewaves-skills": true
  }
}
```

Team members who trust the repository will have the marketplace and plugins automatically available.

## Troubleshooting

### "Marketplace not found"
Ensure you added the marketplace first:
```bash
/plugin marketplace add bluewaves-creations/bluewaves-skills
```

### "Plugin not loading"
Try reinstalling:
```bash
/plugin uninstall epub-generator@bluewaves-skills
/plugin install epub-generator@bluewaves-skills
```

### "HTTPS authentication failed"
If using a private repository, use the SSH URL:
```bash
/plugin marketplace add git@github.com:bluewaves-creations/bluewaves-skills.git
```

## Requirements

- Claude Code CLI
- For epub-generator: Python 3.8+ with ebooklib, markdown, Pillow, beautifulsoup4, lxml, PyYAML
- For athena: Python 3.8+ (stdlib only, no additional packages)
- For docs-factory: Python 3.8+ with xhtml2pdf, reportlab, pypdf, pyhanko, markdown, lxml, pillow, html5lib, cssselect2, matplotlib, numpy
- For skills-factory: `skills-ref` recommended (`uv pip install -e deps/agentskills/skills-ref/`), PyYAML fallback

## License

MIT

## Author

Bluewaves Team (contact@bluewaves.boutique)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.
