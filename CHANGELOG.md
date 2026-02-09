# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.9.0] - 2026-02-09

### Added

#### docs-factory v1.0.0 (new plugin)
- **`brand-bluewaves` skill** — Brand kit for Bluewaves with Merriweather typography, brown sand primary (#B78A66), teal ocean and sun red accents, design tokens, font files, logo variants, PDF page templates with content zones, and decorative patterns
- **`brand-wave-artisans` skill** — Brand kit for Wave Artisans with Nunito Sans typography, gray-driven minimalist palette, design tokens, font files, logo variants, PDF page templates with content zones, and decorative patterns
- **`brand-decathlon` skill** — Brand kit for Decathlon with Inter typography, blue/purple primary (#3643BA), green accent on dark backgrounds only, no rounded corners, design tokens, font files, logo variants, PDF page templates with content zones, and decorative patterns
- **`pdf-factory` skill** — Production-grade PDF rendering engine that converts markdown to professionally typeset PDF using brand kit assets. 6-step pipeline: resolve brand → parse markdown → render content → compose document → validate → sign. Includes render.py (xhtml2pdf + reportlab), compose.py (pypdf page assembly), validate_output.py (QA checks), and install_deps.py
- **`/docs-factory:install-deps` command** — Install Python dependencies for PDF rendering (xhtml2pdf, reportlab, pypdf, pyhanko, markdown, lxml, pillow, html5lib, cssselect2)
- **`/docs-factory:generate-pdf` command** — Full-workflow branded PDF generation from markdown with brand selection, metadata extraction, and validation
- **PDF dependency validation hook** — PreToolUse hook checks Python 3.8+ and required packages before running pdf-factory scripts, sandboxed to pdf-factory paths only
- All three brand kits share 12 semantic colors for status/feedback/categorization
- New `"documents"` category entry for the docs-factory plugin

#### Marketplace
- Marketplace version bumped to 1.9.0
- Total: 6 plugins, 42 skills

---

## [1.8.0] - 2026-02-07

### Added

#### athena v1.0.0 (new plugin)
- **`athena-work` skill** — Process `.athenabrief` research packages exported from the Athena note-taking app. Features progressive disclosure reading order (brief.md → summaries.json → manifest.json → references), short-circuit decision matrix for ~80% early resolution, zero-instruction processing support, and automatic handoff to athena-package for result packaging
- **`athena-package` skill** — Create validated `.athena` import packages for Athena with manifest.json, markdown notes with mandatory header format, aurora energy tags, cross-references, and optional assets. Includes Python validation and creation scripts with validate-fix-revalidate loop
- **`/athena:inspect-package` command** — Inspect contents of `.athenabrief` or `.athena` packages (file listing, manifest preview)
- **`/athena:validate-package` command** — Validate `.athena` packages against the import specification with specific error messages
- **Python dependency validation hook** — PreToolUse hook checks Python 3.8+ availability before running athena scripts
- New `"documents"` category entry for the athena plugin

#### Marketplace
- Marketplace version bumped to 1.8.0
- Total: 5 plugins, 38 skills

---

## [1.7.0] - 2026-02-02

### Added

#### Slash commands for all plugins
- **Project-level:** `/validate-skills` — Validate marketplace skills via skills-ref
- **fal-media:** `/fal-media:check-fal-key` — Check FAL_KEY and test API connectivity; `/fal-media:generate-image` — Quick image generation from a text prompt
- **epub-generator:** `/epub-generator:install-deps` — One-step Python dependency installation and verification
- **swift-apple-dev:** `/swift-apple-dev:check-environment` — Comprehensive Xcode/Swift/SDK readiness audit
- **skills-factory:** `/skills-factory:init-skill` — Scaffold a new skill from template; `/skills-factory:validate-skill` — Validate a skill folder; `/skills-factory:package-skill` — Package a skill into a distributable ZIP

#### skills-factory v1.0.0 (new plugin)
- **`skill-shaper` skill** — Guide for creating effective Agent Skills with bundled scripts, references, and templates. Includes `init_skill.py`, `package_skill.py`, `quick_validate.py`, and 4 reference documents (skill specification, authoring best practices, workflows, output patterns)
- **`gemini-gem-converter` skill** — Knowledge-only skill for converting Agent Skills to Gemini Gems format with platform constraint awareness, 10-file limit strategies, and script-to-docs conversion patterns
- **`openai-gpt-converter` skill** — Knowledge-only skill for converting Agent Skills to Custom GPT format with 8K instruction limit condensation strategies, Code Interpreter evaluation, and Actions mapping
- New `"tools"` category for meta-tooling plugins

#### Marketplace infrastructure
- **`skills-ref` git submodule** at `deps/agentskills/` — Official Anthropic skill validation library pinned as submodule for authoritative SKILL.md validation
- **`scripts/validate-skills.sh`** — Marketplace-wide validation script using `skills-ref validate` against all skills
- **Build script update** — `scripts/build-skill-zips.sh` now includes `scripts/`, `references/`, and `assets/` directories in standalone ZIPs when present

---

## [1.6.1] - 2026-02-02

### Fixed

#### swift-apple-dev
- **Xcode validation hook regex tightened** — anchored to command position to prevent false triggers on `git commit -m "swift..."`, `grep swift`, and similar non-Xcode commands

#### fal-media
- **FAL_KEY validation hook regex consolidated** — added `fal_client` pattern for Python SDK detection alongside existing patterns

---

## [1.6.0] - 2026-01-31

### Added

#### swift-apple-dev v1.2.0
- **`cloudkit` skill** — CloudKit framework for iCloud data storage, sync, and sharing (CKContainer, CKDatabase, CKRecord, CKQuery, subscriptions, CKShare)
- swift-apple-dev now has **22 skills** total

### Fixed

#### epub-generator
- **Narrowed dependency hook regex** to avoid false matches on unrelated commands
- **Active virtualenv detection** — dependency hook now respects already-activated Python virtual environments

### Changed
- Updated README and CLAUDE.md to reflect CloudKit skill addition

---

## [1.5.0] - 2026-01-10

### Added

#### fal-media v1.3.0
- **5 new photographer style skills** with researched prompt templates:
  - `photographer-lindbergh` - Peter Lindbergh style: raw B&W photography, emotional depth, film grain, minimal retouching
  - `photographer-ritts` - Herb Ritts style: sculptural forms, California golden hour, classical Greek influence
  - `photographer-testino` - Mario Testino style: vibrant glamour, bold saturated colors, natural warmth
  - `photographer-lachapelle` - David LaChapelle style: pop surrealism, fluorescent colors, baroque maximalism
  - `photographer-vonunwerth` - Ellen von Unwerth style: playful vintage, film noir influence, feminine empowerment
- **Error handling sections** added to all 5 existing fal-media skills with solution tables
- **Troubleshooting guide** in README with common issues and solutions
- **Prompt engineering tips** for better image generation results

#### epub-generator v1.3.0
- **Dependency validation hook** (`hooks/validate-dependencies.sh`) that blocks execution with helpful messages when packages are missing
- **Pre-validation function** (`validate_sources()`) checks all inputs before processing
- **Post-validation function** (`post_validate_epub()`) with comprehensive output checks
- **Nested table of contents** support with `extract_toc_structure()` for H1/H2/H3 hierarchy
- **Progress reporting** during EPUB generation with chapter-by-chapter status
- **Configurable parameters** including `max_image_size_mb`, `toc_depth`, `custom_css`, and more
- **Complete prerequisites** documentation with macOS/Linux installation commands

### Changed
- fal-media now has **10 skills** (up from 5) including photographer style presets
- epub-generator now has **production-grade validation** with pre/post checks
- Updated all plugin descriptions to reflect new capabilities
- Enhanced keywords for better discoverability

---

## [1.4.0] - 2026-01-09

### Added
- **swift-apple-dev plugin upgraded to v1.1.0** with 6 new enterprise-grade skills:
  - `swiftdata-migration` - Advanced CoreData to SwiftData migration patterns, schema versioning, iCloud conflict resolution
  - `performance-profiling` - Real-world Xcode Instruments case studies, ASAN/TSAN debugging, SwiftUI optimization
  - `macos-development` - macOS Tahoe patterns: window management, menu bars, document apps, Mac Catalyst
  - `visionos-spatial` - Vision Pro development: windows, volumes, immersive spaces, hand tracking, spatial gestures
  - `multiplatform-development` - Cross-platform code sharing, conditional compilation, adaptive layouts
  - `combine-migration` - Combine to Observation/async-await migration patterns

### Changed
- swift-apple-dev now has **21 skills** (up from 15) and **4 specialized agents**
- Updated plugin description to reflect enterprise-grade status
- Enhanced keywords for better discoverability (added visionos, performance, instruments, multiplatform)

## [1.3.0] - 2026-01-09

### Added
- **swift-apple-dev plugin** (v1.0.0) - Comprehensive Apple Swift development skills:
  - **15 Skills** covering iOS 26/macOS Tahoe development:
    - `swift-fundamentals` - Swift 6.x features, macros, Package.swift
    - `swift-concurrency` - Async/await, actors, @MainActor, Sendable
    - `liquid-glass-design` - iOS 26 Liquid Glass design system (~900 lines)
    - `swiftui-patterns` - Modern architecture, @Observable, MV vs MVVM
    - `swiftui-colors-modifiers` - foregroundStyle, gradients, ViewModifiers
    - `animations-transitions` - @Animatable macro, PhaseAnimator, KeyframeAnimator
    - `navigation-menus` - NavigationStack, TabView, toolbars, routing
    - `text-rich-content` - AttributedString, Markdown, rich text editing
    - `swiftdata-persistence` - @Model, @Query, native iCloud sync
    - `foundation-models` - On-device AI with @Generable, tool calling
    - `app-intents` - Siri, Shortcuts, Spotlight, Action Button
    - `widgets-live-activities` - WidgetKit, Live Activities, Dynamic Island
    - `spotlight-discovery` - CoreSpotlight, NSUserActivity
    - `transferable-sharing` - Drag/drop, ShareLink, Universal Clipboard
    - `swift-testing` - Swift Testing framework, @Test, #expect
  - **4 Specialized Agents**:
    - `swift-architect` - Architecture design and code review
    - `swift-designer` - UI/UX review and HIG compliance
    - `swift-qa` - Quality assurance and test strategy
    - `swift-performance` - Profiling with Instruments
  - **Validation hook** for Xcode/Swift installation check

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
