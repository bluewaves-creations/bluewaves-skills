# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bluewaves Skills is a Claude Code plugin marketplace featuring AI-powered media generation and document creation skills. It contains production-grade plugins that extend Claude's capabilities.

## Architecture

```
bluewaves-skills/
├── .claude-plugin/
│   └── marketplace.json          # Central registry of all plugins
├── plugins/
│   ├── fal-media/                # fal.ai media generation (Gemini/Veo)
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/
│   │       ├── gemini-image/SKILL.md
│   │       ├── gemini-image-edit/SKILL.md
│   │       ├── veo-image-to-video/SKILL.md
│   │       ├── veo-reference-video/SKILL.md
│   │       └── veo-frames-to-video/SKILL.md
│   └── epub-generator/           # EPUB ebook generation
│       ├── .claude-plugin/plugin.json
│       └── skills/
│           └── epub-creator/SKILL.md
└── README.md
```

**Key patterns:**
- Each plugin is self-contained in `plugins/[plugin-name]/`
- Skills are defined in `skills/[skill-name]/SKILL.md` with YAML frontmatter
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

## Versioning

All plugins currently sync to version 1.1.0. When updating:
1. Update version in plugin's `.claude-plugin/plugin.json`
2. Update version in `.claude-plugin/marketplace.json`
3. Update CHANGELOG.md
