# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
