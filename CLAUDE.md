# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bluewaves Skills is a Claude Code plugin marketplace featuring Athena document exchange, branded document generation with charts, EPUB creation, and skill creation and cross-platform conversion tools. It contains production-grade plugins that extend Claude's capabilities.

> **Looking for media-factory or web-factory?** Those plugins moved to [bluewaves-skills-rooms](https://github.com/bluewaves-creations/bluewaves-skills-rooms).

## Architecture

```
bluewaves-skills/
├── .claude-plugin/
│   └── marketplace.json          # Central registry of all plugins
├── .claude/
│   └── skills/                   # Project-level skills (validate, build, etc.)
├── plugins/
│   ├── epub-generator/           # EPUB ebook generation
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/
│   │       ├── epub-creator/SKILL.md
│   │       └── install-deps/SKILL.md
│   ├── athena/                   # Athena document exchange
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/
│   │       ├── athena-work/SKILL.md, references/
│   │       ├── athena-package/SKILL.md, references/, scripts/
│   │       ├── inspect-package/SKILL.md
│   │       └── validate-package/SKILL.md
│   ├── docs-factory/              # Branded document generation
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/
│   │       ├── brand-bluewaves/SKILL.md, references/, assets/
│   │       ├── brand-wave-artisans/SKILL.md, references/, assets/
│   │       ├── brand-decathlon/SKILL.md, references/, assets/
│   │       ├── chart-designer/SKILL.md, references/, scripts/
│   │       ├── pdf-factory/SKILL.md, references/, scripts/, assets/
│   │       ├── install-deps/SKILL.md
│   │       └── generate-pdf/SKILL.md
│   └── skills-factory/            # Skill creation & cross-platform conversion
│       ├── .claude-plugin/plugin.json
│       └── skills/
│           ├── skill-shaper/SKILL.md, scripts/, references/
│           ├── skill-eval/SKILL.md, scripts/, references/
│           ├── gemini-gem-converter/SKILL.md, references/
│           ├── openai-gpt-converter/SKILL.md, references/
│           ├── init-skill/SKILL.md
│           ├── validate-skill/SKILL.md
│           ├── package-skill/SKILL.md
│           ├── benchmark-skill/SKILL.md
│           ├── optimize-description/SKILL.md
│           ├── review-evals/SKILL.md
│           └── ship-skill/SKILL.md
├── .github/
│   └── workflows/release.yml    # Tag-triggered release with .skill/.zip assets
├── deps/
│   └── agentskills/              # Git submodule: github.com/agentskills/agentskills
│       └── skills-ref/           # Official skill validation library
└── README.md
```

**Key patterns:**
- Each plugin is self-contained in `plugins/[plugin-name]/`
- Skills are defined in `skills/[skill-name]/SKILL.md` with YAML frontmatter
- User-invocable utility skills use `disable-model-invocation: true` to prevent auto-triggering
- Plugin metadata lives in `.claude-plugin/plugin.json`
- All plugins are registered in `.claude-plugin/marketplace.json`
- Project-level skills live in `.claude/skills/` (validate, build, etc.)

## Plugin Development

### Creating a New Plugin

1. Create directory structure:
   ```
   plugins/your-plugin/
   ├── .claude-plugin/plugin.json
   ├── skills/your-skill/SKILL.md
   └── README.md
   ```

2. Add plugin.json:
   ```json
   {
     "name": "your-plugin",
     "version": "1.0.0",
     "description": "...",
     "author": { "name": "...", "email": "..." },
     "license": "MIT"
   }
   ```

3. Write SKILL.md with YAML frontmatter:
   ```yaml
   ---
   name: skill-name
   description: What this skill does and when Claude should use it
   ---
   # Instructions and examples...
   ```

4. Register in `.claude-plugin/marketplace.json`

### Testing Locally

```bash
# Add local marketplace
/plugin marketplace add /path/to/bluewaves-skills

# Install plugin
/plugin install your-plugin@bluewaves-skills

# Test by triggering the skill
```

## Plugin Prerequisites

- **epub-generator:** Requires `uv pip install ebooklib markdown Pillow beautifulsoup4 lxml`
- **athena:** Python 3.8+ (stdlib only, no additional packages)
- **docs-factory:** Python 3.8+ with xhtml2pdf, reportlab, pypdf, pyhanko, markdown, lxml, pillow, html5lib, cssselect2, matplotlib, numpy
- **skills-factory:** `skills-ref` recommended (`uv pip install -e deps/agentskills/skills-ref/`), PyYAML fallback for `quick_validate.py`

## Building

### Standalone .skill Files

Generate standalone `.skill` files for Claude.ai users (uploads via Settings > Capabilities):

```bash
# Build all skills
bash scripts/build-skill-zips.sh

# Build a single skill
bash scripts/build-skill-zips.sh epub-creator
```

Files are output to `dist/` (gitignored). Each `.skill` file contains `skill-name/SKILL.md` plus any `scripts/`, `references/`, and `assets/` directories.

You can also use the slash command `/build-skill-zips` from Claude Code.

### Skill Validation

Validate skills using the official `skills-ref` library (pinned as git submodule at `deps/agentskills/`):

```bash
# Install skills-ref from submodule
git submodule update --init
uv pip install -e deps/agentskills/skills-ref/

# Validate all skills in the marketplace
bash scripts/validate-skills.sh

# Validate a single skill
bash scripts/validate-skills.sh skill-shaper
```

To update the submodule: `git submodule update --remote deps/agentskills`

## Releasing

Releases are automated via GitHub Actions. Push a version tag to create a release with `.skill` and `.zip` assets:

```bash
git tag v4.1.0
git push --tags
```

The workflow builds all `.skill` files, creates `.zip` copies, and publishes them as GitHub Release assets with auto-generated release notes.

## Versioning

Current marketplace version: 4.1.0

When updating:
1. Update version in plugin's `.claude-plugin/plugin.json`
2. Update version in `.claude-plugin/marketplace.json`
3. Update CHANGELOG.md
