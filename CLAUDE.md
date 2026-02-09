# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bluewaves Skills is a Claude Code plugin marketplace featuring AI-powered media generation, document creation, and Swift development skills. It contains production-grade plugins that extend Claude's capabilities.

## Architecture

```
bluewaves-skills/
├── .claude-plugin/
│   └── marketplace.json          # Central registry of all plugins
├── plugins/
│   ├── fal-media/                # fal.ai media generation (Gemini/Veo)
│   │   ├── .claude-plugin/plugin.json
│   │   ├── commands/             # check-fal-key, generate-image
│   │   └── skills/
│   │       ├── gemini-image/SKILL.md
│   │       ├── gemini-image-edit/SKILL.md
│   │       ├── veo-image-to-video/SKILL.md
│   │       ├── veo-reference-video/SKILL.md
│   │       └── veo-frames-to-video/SKILL.md
│   ├── epub-generator/           # EPUB ebook generation
│   │   ├── .claude-plugin/plugin.json
│   │   ├── commands/             # install-deps
│   │   └── skills/
│   │       └── epub-creator/SKILL.md
│   ├── athena/                   # Athena document exchange (2 skills)
│   │   ├── .claude-plugin/plugin.json
│   │   ├── commands/             # inspect-package, validate-package
│   │   ├── hooks/hooks.json
│   │   └── skills/
│   │       ├── athena-work/SKILL.md, references/
│   │       └── athena-package/SKILL.md, references/, scripts/
│   ├── swift-apple-dev/          # Apple Swift development (22 skills, 4 agents)
│   │   ├── .claude-plugin/plugin.json
│   │   ├── commands/             # check-environment
│   │   ├── hooks/hooks.json
│   │   ├── agents/
│   │   │   ├── swift-architect.md
│   │   │   ├── swift-designer.md
│   │   │   ├── swift-qa.md
│   │   │   └── swift-performance.md
│   │   └── skills/
│   │       ├── swift-fundamentals/SKILL.md
│   │       ├── swift-concurrency/SKILL.md
│   │       ├── swift-testing/SKILL.md
│   │       ├── liquid-glass-design/SKILL.md
│   │       ├── swiftui-patterns/SKILL.md
│   │       ├── swiftui-colors-modifiers/SKILL.md
│   │       ├── animations-transitions/SKILL.md
│   │       ├── navigation-menus/SKILL.md
│   │       ├── text-rich-content/SKILL.md
│   │       ├── swiftdata-persistence/SKILL.md
│   │       ├── swiftdata-migration/SKILL.md
│   │       ├── foundation-models/SKILL.md
│   │       ├── app-intents/SKILL.md
│   │       ├── widgets-live-activities/SKILL.md
│   │       ├── spotlight-discovery/SKILL.md
│   │       ├── transferable-sharing/SKILL.md
│   │       ├── performance-profiling/SKILL.md
│   │       ├── macos-development/SKILL.md
│   │       ├── visionos-spatial/SKILL.md
│   │       ├── multiplatform-development/SKILL.md
│   │       ├── combine-migration/SKILL.md
│   │       └── cloudkit/SKILL.md
│   ├── docs-factory/              # Branded document generation (4 skills)
│   │   ├── .claude-plugin/plugin.json
│   │   ├── commands/              # install-deps, generate-pdf
│   │   ├── hooks/hooks.json
│   │   └── skills/
│   │       ├── brand-bluewaves/SKILL.md, references/, assets/
│   │       ├── brand-wave-artisans/SKILL.md, references/, assets/
│   │       ├── brand-decathlon/SKILL.md, references/, assets/
│   │       └── pdf-factory/SKILL.md, references/, scripts/, assets/
│   └── skills-factory/            # Skill creation & cross-platform conversion (3 skills)
│       ├── .claude-plugin/plugin.json
│       ├── commands/              # init-skill, validate-skill, package-skill
│       └── skills/
│           ├── skill-shaper/SKILL.md, scripts/, references/
│           ├── gemini-gem-converter/SKILL.md, references/
│           └── openai-gpt-converter/SKILL.md, references/
├── deps/
│   └── agentskills/              # Git submodule: github.com/agentskills/agentskills
│       └── skills-ref/           # Official skill validation library
└── README.md
```

**Key patterns:**
- Each plugin is self-contained in `plugins/[plugin-name]/`
- Skills are defined in `skills/[skill-name]/SKILL.md` with YAML frontmatter
- Commands are defined in `commands/[command-name].md` with `description` YAML frontmatter
- Plugin metadata lives in `.claude-plugin/plugin.json`
- All plugins are registered in `.claude-plugin/marketplace.json`

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

- **fal-media:** Requires `FAL_KEY` environment variable (fal.ai API key)
- **epub-generator:** Requires `uv pip install ebooklib markdown Pillow beautifulsoup4 lxml`
- **swift-apple-dev:** Requires Xcode 26+ with Swift 6 toolchain
- **athena:** Python 3.8+ (stdlib only, no additional packages)
- **docs-factory:** Python 3.8+ with xhtml2pdf, reportlab, pypdf, pyhanko, markdown, lxml, pillow, html5lib, cssselect2
- **skills-factory:** `skills-ref` recommended (`uv pip install -e deps/agentskills/skills-ref/`), PyYAML fallback for `quick_validate.py`

## Building

### Standalone Skill ZIPs

Generate standalone ZIP files for Claude.ai users (uploads via Settings > Capabilities):

```bash
# Build all skills
bash scripts/build-skill-zips.sh

# Build a single skill
bash scripts/build-skill-zips.sh gemini-image
```

ZIPs are output to `dist/` (gitignored). Each ZIP contains `skill-name/SKILL.md` plus any `scripts/`, `references/`, and `assets/` directories.

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

## Versioning

Current marketplace version: 1.9.0

When updating:
1. Update version in plugin's `.claude-plugin/plugin.json`
2. Update version in `.claude-plugin/marketplace.json`
3. Update CHANGELOG.md
