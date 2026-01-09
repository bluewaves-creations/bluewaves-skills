# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-01-09

### Changed
- **Enterprise upgrade** to align with latest Claude Code plugin specifications:
  - Added `metadata` section to marketplace.json with description and version
  - Enriched plugin entries with full metadata (author, homepage, repository, license, keywords, category)
  - Added `homepage` and `bugs` fields to all plugin.json files
  - Synchronized all versions to 1.1.0 (was mismatched between marketplace and plugins)

### Added
- **Security hardening** via `allowed-tools` in all SKILL.md frontmatter
  - Restricts Claude's tool access to Bash, Read, Write when skills are active
- **Validation hooks** for fal-media plugin
  - PreToolUse hook validates FAL_KEY environment variable before API calls
  - Blocks commands with helpful error message if key is missing

## [1.1.0] - 2025-12-10

### Changed
- **epub-creator skill** completely rewritten for production-grade quality:
  - 5-step workflow: Pre-process → Convert → Assemble → Validate → Deliver
  - Automatic markdown quirk fixes (line endings, headings, emphasis, links)
  - Smart title extraction from YAML frontmatter, headings, or filename
  - Cover image validation and auto-optimization
  - Image validation with size optimization
  - Professional CSS typography
  - EPUB validation with epubcheck
  - QA checklist with detailed reporting
  - JSON report generation for each build

### Added
- `limit_generations` parameter to gemini-image and gemini-image-edit skills

## [1.0.0] - 2025-12-10

### Added
- Initial release of Bluewaves Skills marketplace
- **fal-media plugin** (v1.0.0) with 5 skills:
  - `gemini-image` - Text-to-image generation using Gemini 3 Pro
  - `gemini-image-edit` - Image editing with text prompts
  - `veo-image-to-video` - Animate single images into video
  - `veo-reference-video` - Generate video with consistent subject appearance
  - `veo-frames-to-video` - Create video from first and last frame images
- **epub-generator plugin** (v1.0.0) with 1 skill:
  - `epub-creator` - Generate validated EPUB from markdown files and images
- Marketplace documentation:
  - README with installation, usage, and troubleshooting
  - CONTRIBUTING guide for adding new plugins
  - MIT License
- Team distribution support via `.claude/settings.json`
