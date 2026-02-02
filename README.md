# Bluewaves Skills

![Version](https://img.shields.io/badge/version-1.7.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A Claude Code plugin marketplace featuring AI-powered media generation, document creation, enterprise-grade Swift development, and skill creation and cross-platform conversion tools.

## Installation

Add this marketplace to Claude Code:

```bash
/plugin marketplace add bluewaves-creations/bluewaves-skills
```

## Available Plugins

### swift-apple-dev

Enterprise-grade Apple Swift development skills for iOS 26, macOS Tahoe, visionOS, and cross-platform apps.

```bash
/plugin install swift-apple-dev@bluewaves-skills
```

**22 Skills organized by category:**

| Category | Skills |
|----------|--------|
| **Core Swift** | `swift-fundamentals`, `swift-concurrency`, `swift-testing` |
| **SwiftUI & Design** | `liquid-glass-design`, `swiftui-patterns`, `swiftui-colors-modifiers`, `animations-transitions` |
| **Data & AI** | `swiftdata-persistence`, `swiftdata-migration`, `foundation-models` |
| **Cloud & Sync** | `cloudkit` |
| **Navigation & Content** | `navigation-menus`, `text-rich-content`, `app-intents`, `widgets-live-activities`, `spotlight-discovery`, `transferable-sharing` |
| **Platform-Specific** | `macos-development`, `visionos-spatial`, `multiplatform-development` |
| **Migration & Performance** | `combine-migration`, `performance-profiling` |

**4 Specialized Agents:**
- `swift-architect` - Architecture design and code review
- `swift-designer` - UI/UX review and HIG compliance
- `swift-qa` - Quality assurance and test strategy
- `swift-performance` - Profiling with Instruments

**Prerequisites:** Xcode 26+ with Swift 6 toolchain

---

### fal-media

AI-powered media generation using fal.ai's Gemini and Veo models, plus 5 photographer style skills.

```bash
/plugin install fal-media@bluewaves-skills
```

**10 Skills:**

| Category | Skills |
|----------|--------|
| **Image Generation** | `gemini-image`, `gemini-image-edit` |
| **Video Generation** | `veo-image-to-video`, `veo-reference-video`, `veo-frames-to-video` |
| **Photographer Styles** | `photographer-lindbergh`, `photographer-ritts`, `photographer-testino`, `photographer-lachapelle`, `photographer-vonunwerth` |

**Photographer Styles:**
- **Lindbergh** - Raw B&W photography, emotional depth, film grain
- **Ritts** - Sculptural forms, California golden hour, classical Greek
- **Testino** - Vibrant glamour, bold saturated colors
- **LaChapelle** - Pop surrealism, fluorescent colors, baroque maximalism
- **von Unwerth** - Playful vintage, film noir, feminine empowerment

**Prerequisites:** Set `FAL_KEY` environment variable in `~/.zshrc`

---

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

### skills-factory

Skill creation, validation, and cross-platform conversion tools for Agent Skills.

```bash
/plugin install skills-factory@bluewaves-skills
```

**3 Skills:**

| Category | Skills |
|----------|--------|
| **Skill Creation** | `skill-creator` |
| **Cross-Platform Conversion** | `gemini-gem-converter`, `openai-gpt-converter` |

- **skill-creator** - Create effective Agent Skills with guided workflows, bundled scripts, and reference materials
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

### fal-media

| Command | Description |
|---------|-------------|
| `/fal-media:check-fal-key` | Check if FAL_KEY is set and test API connectivity |
| `/fal-media:generate-image <prompt>` | Quick image generation from a text prompt |

### epub-generator

| Command | Description |
|---------|-------------|
| `/epub-generator:install-deps` | Install Python dependencies (uses `uv` by default, `--pip` for pip) |

### swift-apple-dev

| Command | Description |
|---------|-------------|
| `/swift-apple-dev:check-environment` | Audit Xcode, Swift, SDKs, and simulators |

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

Each ZIP contains a single skill with its instructions. All 36 skills are available individually.

> **Note:** Plugin hooks (API key validation, Xcode version checks) are Claude Code-only features and won't apply when using skills directly in Claude.ai.

---

## Usage Examples

```
# Swift development
"Create a SwiftUI view with Liquid Glass design"
"Help me migrate from CoreData to SwiftData"
"Profile my app for memory leaks"

# Generate an image
"Create a 4K image of a cyberpunk city at night"

# Edit an image
"Add rain and dramatic lighting to this photo"

# Create video from image
"Animate this landscape with flowing water and wind"

# Generate EPUB
"Create an EPUB from the markdown files in ./chapters"

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
/plugin uninstall swift-apple-dev@bluewaves-skills
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
    "swift-apple-dev@bluewaves-skills": true,
    "fal-media@bluewaves-skills": true,
    "epub-generator@bluewaves-skills": true,
    "skills-factory@bluewaves-skills": true
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

### "FAL_KEY not set"
Add to your `~/.zshrc`:
```bash
export FAL_KEY="your-api-key"
```
Then restart your terminal or run `source ~/.zshrc`.

### "Plugin not loading"
Try reinstalling:
```bash
/plugin uninstall swift-apple-dev@bluewaves-skills
/plugin install swift-apple-dev@bluewaves-skills
```

### "HTTPS authentication failed"
If using a private repository, use the SSH URL:
```bash
/plugin marketplace add git@github.com:bluewaves-creations/bluewaves-skills.git
```

## Requirements

- Claude Code CLI
- For swift-apple-dev: Xcode 26+ with Swift 6
- For fal-media: fal.ai API key (`FAL_KEY`)
- For epub-generator: Python 3.8+ with ebooklib, markdown, Pillow, beautifulsoup4, lxml, PyYAML
- For skills-factory: `skills-ref` recommended (`uv pip install -e deps/agentskills/skills-ref/`), PyYAML fallback

## License

MIT

## Author

Bluewaves Team (contact@bluewaves.boutique)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.
