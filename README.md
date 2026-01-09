# Bluewaves Skills

![Version](https://img.shields.io/badge/version-1.4.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A Claude Code plugin marketplace featuring AI-powered media generation, document creation, and enterprise-grade Swift development skills.

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

**21 Skills organized by category:**

| Category | Skills |
|----------|--------|
| **Core Swift** | `swift-fundamentals`, `swift-concurrency`, `swift-testing` |
| **SwiftUI & Design** | `liquid-glass-design`, `swiftui-patterns`, `swiftui-colors-modifiers`, `animations-transitions` |
| **Data & AI** | `swiftdata-persistence`, `swiftdata-migration`, `foundation-models` |
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

AI-powered media generation using fal.ai's Gemini and Veo models.

```bash
/plugin install fal-media@bluewaves-skills
```

**Skills:**
- `gemini-image` - Generate images from text prompts
- `gemini-image-edit` - Edit images with text instructions
- `veo-image-to-video` - Animate images into videos
- `veo-reference-video` - Generate video with consistent subjects
- `veo-frames-to-video` - Create video from first/last frames

**Prerequisites:** Set `FAL_KEY` environment variable in `~/.zshrc`

---

### epub-generator

Generate validated EPUB 3 ebooks from markdown and images.

```bash
/plugin install epub-generator@bluewaves-skills
```

**Skills:**
- `epub-creator` - Convert markdown files to EPUB with cover, TOC, and styling

**Prerequisites:** `uv pip install ebooklib markdown`

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
    "epub-generator@bluewaves-skills": true
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
- For epub-generator: Python with ebooklib

## License

MIT

## Author

Bluewaves Team (contact@bluewaves.boutique)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.
