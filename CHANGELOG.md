# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.7.1] - 2026-02-18

### Fixed

- **podcast-generator** — Use foreground execution for Claude.ai sandbox (nohup background processes silently die in the container); Claude Code retains the nohup background approach

### Marketplace

- Marketplace version bumped to 2.7.1

---

## [2.7.0] - 2026-02-18

### Added

- **podcast-generator** — Cloudflare AI Gateway proxy support: routes Gemini TTS calls through CF AI Gateway with `cf-aig-authorization` header for usage tracking and rate limiting
- **podcast-generator** — `### BREAK` markers for splitting long dialogs into independently generated audio segments with optional `[hint text]` for continuation context
- **build script** — Gateway credential injection (`gateway_url`, `gateway_token`) for podcast-generator when using `--user` flag

### Changed

- **podcast-generator** — Lowered per-chunk word limit from 1500 to 1200 words for safer Gemini TTS ceiling margin
- **podcast-generator** — Enabled unbuffered stdout (`line_buffering=True`) for real-time log output
- **keys.example.json** — Renamed `ai_gateway_url` → `ai_gateway_name` for clarity
- media-factory plugin version bumped to 2.3.0

### Marketplace

- Marketplace version bumped to 2.7.0

---

## [2.6.0] - 2026-02-18

### Changed

- **build script** — Output files now use `.skill` extension instead of `.zip` (still ZIP archives internally), aligning with skills-factory `package_skill.py` convention.
- **Marketplace-wide skill audit** — Refactored all 10 fal.ai skills to extract shared boilerplate (prerequisites, Python examples, response formats, error handling) into `plugins/media-factory/references/fal-api.md`. Each skill now references the shared file via symlink, reducing per-skill line count by ~50%. Follows progressive disclosure best practices from skill-shaper v2.4.0.
- **pdf-factory** — Extracted 110-line "How It Works" internals section to `references/internals.md` with on-demand load condition. SKILL.md reduced from 335 to ~225 lines.
- **chart-designer** — Added "when to read" load conditions to reference file links per progressive disclosure rules.
- **Brand kit descriptions** — Tightened brand-bluewaves, brand-decathlon, and brand-wave-artisans YAML descriptions to single-line format, removing implementation detail.
- **site-factory / site-publisher** — Tightened YAML descriptions, removing implementation detail.
- **podcast-generator** — Condensed Dialog Crafting Guidelines from ~52 lines to ~15 lines with pointer to `references/tts-prompting-guide.md`.
- media-factory plugin version bumped to 2.2.0

### Marketplace

- Marketplace version bumped to 2.6.0

---

## [2.5.0] - 2026-02-18

### Added

- **media-factory (podcast-generator)** — New skill for generating two-host podcast episodes using Google Gemini TTS. Features Athena & Gizmo AI co-hosts with distinct voices, automatic long-dialog splitting and concatenation, source document extraction (.md/.pdf), and expressive director's notes system for natural-sounding dialog delivery.
- **media-factory** — Gemini API key validation hook (`validate-gemini-key.sh`) mirroring the existing fal.ai key validation pattern
- **build script** — Gemini credential injection support for podcast-generator skill ZIPs (`--user` flag)

### Changed

- media-factory plugin version bumped to 2.1.0
- media-factory description and keywords updated to include podcast/Gemini TTS/audio generation

### Marketplace

- Marketplace version bumped to 2.5.0

---

## [2.4.0] - 2026-02-18

### Added

- **skills-factory (skill-shaper)** — Three new reference guides for the skill-shaper skill:
  - `testing-and-debugging.md` — Comprehensive testing strategies, validation workflows, and debugging patterns for skill development
  - `skill-categories.md` — Taxonomy of skill categories with characteristics, examples, and design considerations
  - `distribution-guide.md` — Distribution formats, packaging strategies, and cross-platform conversion guidance

### Changed

- **skills-factory (skill-shaper)** — Enhanced SKILL.md with improved structure, updated section references, and clearer authoring guidance
- **skills-factory (skill-shaper)** — Expanded `authoring-best-practices.md` with additional patterns and refined recommendations
- **skills-factory (skill-shaper)** — Updated `workflows.md` with broader workflow coverage and improved examples
- skills-factory plugin version bumped to 1.1.0

### Marketplace

- Marketplace version bumped to 2.4.0

---

## [2.3.4] - 2026-02-12

### Changed

- **docs-factory** — Updated page-blank and page-content PDF templates for brand-bluewaves.

---

## [2.3.3] - 2026-02-12

### Changed

- **docs-factory** — Replaced PDF page templates for brand-bluewaves and brand-wave-artisans with updated designs (covers, section dividers, color pages, content pages).

---

## [2.3.2] - 2026-02-12

### Fixed

- **web-factory** — Added `User-Agent: site-publisher/1.0` header to `site_api.py` HTTP requests, fixing Cloudflare **error 1010** (bot detected) that blocked Python's default `User-Agent: Python-urllib/3.x`.
- **web-factory** — Fixed missed apex domain default in `cf_utils.py`: `"bluewaves-athena.app"` → `"api.bluewaves-athena.app"` (same fix applied to `site_api.py` in v2.3.1).

---

## [2.3.1] - 2026-02-12

### Fixed

- **web-factory** — Default gateway domain changed from `bluewaves-athena.app` (apex, no DNS record) to `api.bluewaves-athena.app` (matches wildcard `*.bluewaves-athena.app`), fixing `dns_no_records` errors for Claude.ai standalone ZIP users calling `site_api.py`.

---

## [2.3.0] - 2026-02-12

### Added

#### web-factory v1.0.0 (new plugin)
- **Hono gateway Worker** — Single Cloudflare Worker on `*.bluewaves-athena.app` serving password-protected branded websites from R2 with HMAC cookie-based authentication
- **Admin API** (`/_api/`) — RESTful endpoints for publishing, updating, listing, downloading, deleting sites, and rotating passwords. Bearer token auth with support for super-admin secret and per-user API keys stored in KV
- **`site-factory` skill** — Build single-page HTML from markdown with a built-in neutral default brand (system fonts, gray palette) or optional docs-factory brand kit. Maps design tokens to CSS custom properties, generates responsive layout with header, TOC, content, attachments, and footer
- **`site-publisher` skill** — Publish and manage sites via Python HTTP client (`site_api.py`, stdlib-only). Works in both Claude Code and Claude.ai standalone ZIPs
- **Python HTTP client** (`site_api.py`) — Stdlib-only admin API client supporting publish, update, download, list, info, delete, and rotate-password operations
- **Download endpoint** (`GET /sites/{brand}/{name}/files`) — Download all site files as base64 for round-trip editing workflows
- **Credential utilities** (`cf_utils.py`) — Dual-mode credential resolution (credentials.json for Claude.ai, env vars for Claude Code) for both gateway and Cloudflare API access
- **6 slash commands:** `/web-factory:install-deps`, `/web-factory:check-cf-key`, `/web-factory:setup-gateway`, `/web-factory:create-api-key`, `/web-factory:list-api-keys`, `/web-factory:revoke-api-key`
- **PreToolUse hook** — Validates credentials before wrangler/site_api commands
- **Passphrase generator** — System-generated 4-word passphrases (e.g. `coral-sunset-tide-2026`) using CSPRNG
- **Branded login page** — Clean, mobile-friendly form with CSS custom properties from brand kit tokens
- **Default brand** — Built-in neutral brand (gray palette, system fonts, Bluewaves logo) so sites work without a docs-factory brand kit
- **Skeleton template polish** — Smooth scrolling for TOC navigation, floating back-to-top button (icon-only, appears after 300px scroll), smaller header title (h2 size), logo-left/text-right footer layout, print-safe (button hidden in print media)

#### Marketplace
- Marketplace version bumped to 2.3.0
- Total: 6 plugins, 23 skills

---

## [2.2.0] - 2026-02-11

### Changed

- **docs-factory (chart-designer)** — Stripped to design-system core. Removed `render_chart.py` JSON CLI renderer (261 lines, 10 hardcoded chart type functions) that constrained rather than empowered. The skill now follows pdf-factory's philosophy: provide the design system (`load_theme()`, `theme.apply()`, named figure sizes), get out of the way. Claude writes standard matplotlib code; the theme handles brand colors, typography, and sizing.
- **docs-factory (chart-designer)** — Rewrote SKILL.md as Python-first design-system documentation with How It Works (3 value-props), compact API Reference, and references to the chart-types cookbook.
- **docs-factory (chart-designer)** — Rewrote `references/chart-types.md` as pure matplotlib cookbook: removed all JSON spec blocks, added complete runnable Python examples for all 10 chart types within `with theme.apply():`, added practical tips per chart type.
- **docs-factory (chart-designer)** — Cleaned up `chart_theme.py`: removed CLI `main()` function and `if __name__` block (~25 lines). Public API unchanged: `load_theme()`, `ChartTheme.apply()`, `BrandPalette`, `FIGURE_SIZES`.

### Removed

- **docs-factory (chart-designer)** — `scripts/render_chart.py` deleted entirely. The JSON spec parser, 10 chart renderer functions, and CLI dispatcher are no longer needed.

---

## [2.1.2] - 2026-02-11

### Fixed

- **media-factory** — Credential lookup order flipped: `credentials.json` is now checked before `$FAL_KEY` env var in `fal_utils.py`, `validate-fal-key.sh` hook, and all 10 SKILL.md files. Standalone ZIP users no longer need an env var when a bundled `credentials.json` is present.
- **docs-factory (chart-designer)** — Pie/donut charts with small slices (< 5%) now use legend mode instead of inline labels, preventing text overlap. Percentage labels are suppressed on tiny slices; a below-chart legend shows `"Category (X%)"` or `"Category (<1%)"` per entry.
- **docs-factory (pdf-factory)** — H1 titles no longer duplicate between section divider pages and content pages. New `--sections` CLI flag on `render.py` replaces matched H1 headings with invisible text markers so compose.py still detects sections while the visible title appears only on the divider.

### Added

- **docs-factory** — `tokens.imagery.pdf_defaults` added to all 3 brand kit manifests (`resolution: "2K"`, `output_format: "jpeg"`, `enable_web_search: true`) so the image generation skill produces PDF-optimized images instead of 7MB PNGs.
- **docs-factory (pdf-factory)** — New "Image Generation" section documenting how to read `tokens.imagery.pdf_defaults` from the active brand kit for PDF-optimized image settings.
- **docs-factory (chart-designer)** — QA checklist: 6-point verification for labels, data accuracy, legends, clipping, contextual fit, and brand consistency.
- **docs-factory (pdf-factory)** — Enhanced Step 5 with 7-point manual QA checklist covering H1 duplication, image relevance, brand alignment, chart readability, file size, page flow, and cover/divider zones.

---

## [2.1.1] - 2026-02-10

### Fixed

- **media-factory** — Standalone skill ZIPs now include shared Python scripts (`fal_generate.py`, `fal_utils.py`, `credentials.example.json`). Previously all 10 media-factory ZIPs shipped with only SKILL.md, making them non-functional as Claude.ai uploads. Added symlinked `scripts/` directories in each skill pointing to the shared plugin-level scripts, updated `build-skill-zips.sh` to follow symlinks (`cp -rL`), and fixed CLI paths in 5 SKILL.md files from `plugins/media-factory/scripts/` to relative `scripts/`.
- **media-factory** — Added `credentials.example.json` with sentinel value and updated 5 photographer SKILL.md files with copy-from-example instructions.
- Added `credentials.json` to `.gitignore` to prevent accidental API key commits.

---

## [2.1.0] - 2026-02-10

### Removed

- **`swift-apple-dev` plugin** (22 skills, 4 agents) — Apple has integrated Claude Code with Xcode and provides complete Swift documentation access via MCP, making this plugin redundant. Users who need Swift development support should use Xcode's built-in Claude Code integration instead.

### Changed

- Marketplace version bumped to 2.1.0
- Total: 5 plugins, 21 skills

---

## [2.0.0] - 2026-02-10

### Breaking Changes

- **Renamed `fal-media` plugin to `media-factory`** — update install commands from `fal-media@bluewaves-skills` to `media-factory@bluewaves-skills`
- **Renamed skills**: `gemini-image` → `image-generator`, `gemini-image-edit` → `image-editor`, `veo-image-to-video` → `video-from-image`, `veo-reference-video` → `video-from-reference`, `veo-frames-to-video` → `video-from-frames`
- **Removed cURL examples** from all media-factory skills — Python `fal_client` is now the only supported approach

### Added

- **`chart-designer` skill** in docs-factory: brand-consistent matplotlib chart generation with 10 chart types (bar, grouped_bar, stacked_bar, horizontal_bar, line, area, pie, donut, scatter, heatmap), `chart_theme.py` brand config loader, and `render_chart.py` CLI renderer
- **Chart tokens** (`tokens.chart`) in all 3 brand kits: categorical/sequential/diverging color palettes, axis/grid styling, typography mappings referencing brand type_scale and colors
- **Imagery guidelines** (`tokens.imagery`) in all 3 brand kits: photography style, corner radius, AI prompt templates with grounding references
- **SVG pre-processing** in PDF Factory: inline and referenced SVGs auto-converted to high-DPI PNG via svglib (no new dependencies)
- **Image corner radius** support in PDF Factory via Pillow: Decathlon 0pt, Bluewaves 6pt, Wave Artisans 4pt
- **Python `fal_client` integration** in media-factory: `fal_generate.py` unified generation script and `fal_utils.py` shared utilities (replaces raw cURL)
- **`install-deps` command** for media-factory: installs `fal-client` package
- **API key support via `credentials.json`** for Claude.ai standalone ZIP users
- **`figure`/`figcaption` CSS** in base.css for chart captions

### Fixed

- **pdf-factory** — `_preprocess_figures` now uses regex to handle `<figure>` and `<figcaption>` tags with attributes (e.g. `<figure class="chart">`); previously only matched bare tags
- **pdf-factory** — `_preprocess_code_blocks` now preserves attributes on `<pre>` and `<code>` tags and strips leading/trailing newlines before `<br/>` conversion to eliminate spurious whitespace
- **pdf-factory** — `_preprocess_image_widths` uses `re.escape()` on captured width values to prevent latent regex injection
- **chart-designer** — Legend columns capped at 4 (`ncol=min(len(series_list), 4)`) across bar, horizontal_bar, line, and scatter renderers to prevent horizontal overflow with 5+ series

### Improved

- media-factory skills: queue-based requests via `fal_client.subscribe()`, progress logging via `on_queue_update`, proper error handling with fal_client exception types, timeout support
- media-factory: timestamped output filenames, platform-aware file opening, `sync_mode` for reliable image delivery, `enable_web_search: true` for style grounding
- media-factory photographer skills: unified endpoint from `fal-ai/gemini-pro` to `fal-ai/gemini-3-pro-image-preview`, `enable_web_search: true` for photographer style grounding
- media-factory hooks: credentials file check alongside env var

---

## [1.9.3] - 2026-02-10

### Fixed

- **docs-factory** — Forgive unused font roles in pdf-factory validator. When a role's font (e.g., `mono`/Fira Code) isn't embedded because the PDF content doesn't use it (no code blocks), the validator no longer flags it as missing. Added `unused_roles` set that detects when none of a role's typeface names appear anywhere in the PDF fonts, treating the role as unused rather than unmatched.

## [1.9.2] - 2026-02-09

### Fixed

- **docs-factory** — Fixed false-negative font-role validation in `validate_output.py`. The brand fonts check incorrectly flagged fonts as missing because xhtml2pdf embeds fonts by their internal typeface name (e.g. `Inter-Bold`) rather than the role-based registration name (e.g. `Brand-heading-bold`). Added `_read_ttf_names()` helper that reads TTF name tables (stdlib `struct`, no new dependencies) to build a role-to-typeface mapping, matching embedded PDF font names against expected typeface names. Removed the broad `len(custom_fonts) >= len(expected_roles)` fallback that masked the issue.

## [1.9.1] - 2026-02-09

### Changed

- **docs-factory** — Replaced 1,512 bundled Phosphor SVG icons with on-demand `fetch_icons.py` script that downloads from unpkg CDN. Reduces plugin file count from 1,625 to 114, unblocking the 200-file validation limit.
- Updated brand manifests (bluewaves, decathlon, wave-artisans) with CDN `source` URL and `local` path for icon resolution
- Added Icons section to pdf-factory SKILL.md documenting the fetch workflow
- Gitignored fetched icons directory

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

#### Marketplace-wide audit
- Added `license: MIT` to all 42 SKILL.md frontmatters for standalone distribution
- Added `compatibility` field to 37 skills with environment requirements (FAL_KEY, Xcode 26+, Python 3.8+, skills-ref)
- Split epub-creator SKILL.md from 1225 lines to 134 + 5 reference files (500-line best practice)
- Fixed `quick_validate.py` to accept the `compatibility` property per the skill specification
- Bundled Phosphor regular-weight icon set in pdf-factory for document iconography

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
