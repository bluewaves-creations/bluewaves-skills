---
name: epub-creator
description: Create production-quality EPUB 3 ebooks from markdown and images with automated QA, formatting fixes, and validation. Use when creating ebooks, converting markdown to EPUB, or compiling chapters into a publishable book. Handles markdown quirks, generates TOC, adds covers, and validates output automatically.
allowed-tools: Bash, Read, Write
license: MIT
compatibility: Python 3.8+ with ebooklib, markdown, Pillow, beautifulsoup4, lxml
---

# EPUB Creator (Production Grade)

Create validated, publication-ready EPUB 3 ebooks from markdown files and images.

## Prerequisites

**Python Version**: Requires Python 3.8 or higher

```bash
# Install all required packages
uv pip install ebooklib markdown Pillow beautifulsoup4 lxml PyYAML

# Or with pip
pip install ebooklib markdown Pillow beautifulsoup4 lxml PyYAML
```

**Optional** (for EPUB validation):
```bash
# macOS
brew install epubcheck

# Linux (Debian/Ubuntu)
apt install epubcheck

# Via Python wrapper
uv pip install epubcheck
```

## Production Workflow

Follow this 5-step workflow to create high-quality EPUBs:

```
1. PRE-PROCESS → 2. CONVERT → 3. ASSEMBLE → 4. VALIDATE → 5. DELIVER
```

### Step 1: Pre-Processing (Input Validation & Fixes)

Gather inputs, fix markdown quirks (line endings, heading levels, unclosed emphasis, broken links), validate and optimize images, and validate cover dimensions (minimum 1400x2100px, ~1:1.5 aspect ratio).

See `references/pre-processing.md` for full implementation with `gather_inputs()`, `fix_markdown_quirks()`, `validate_and_fix_images()`, `validate_cover()`, and `validate_sources()`.

### Step 2: Content Conversion

Extract YAML frontmatter metadata, smart-extract chapter titles (frontmatter > first heading > filename), convert markdown to valid EPUB XHTML with robust extensions (tables, fenced code, smart quotes, sane lists), and build hierarchical ToC structure with configurable depth (H1/H2/H3).

See `references/content-conversion.md` for full implementation with `extract_frontmatter()`, `extract_title()`, `markdown_to_xhtml()`, `extract_toc_structure()`, and `build_nested_toc()`.

### Step 3: EPUB Assembly

Apply professional CSS stylesheet (typography, headings, paragraphs, code blocks, tables, images), build the complete EPUB with `ebooklib` including metadata, cover, chapters, images, TOC, and spine.

See `references/epub-assembly.md` for full implementation with `EPUB_CSS` and `create_production_epub()`.

### Step 4: Validation & QA

Run epubcheck (with fallback to basic ZIP structure validation), comprehensive post-validation (file size, mimetype, container.xml, XHTML content, styles, images), and a QA checklist summarizing pass/fail/warnings.

See `references/validation-qa.md` for full implementation with `validate_epub()`, `post_validate_epub()`, and `qa_checklist()`.

### Step 5: Complete Production Script

End-to-end orchestration: auto-detect cover, create EPUB, run QA, print report, save JSON report alongside the EPUB.

See `references/production-script.md` for full implementation with `create_epub_production()`.

---

## Usage Examples

### Basic Usage
```
"Create an EPUB from the markdown files in ./chapters"
```
Claude will:
1. Scan for markdown files
2. Fix any formatting issues
3. Generate TOC from headings
4. Create styled EPUB
5. Validate and report

### With Cover Image
```
"Create an EPUB called 'My Novel' from ./book with cover.jpg as the cover"
```

### Full Metadata
```
"Create an EPUB from ./manuscript:
- Title: The Great Adventure
- Author: Jane Smith
- Language: English
- Publisher: Indie Press"
```

### QA Mode
```
"Create an EPUB from ./draft and show me all the issues found"
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No markdown files found" | Ensure `.md` files exist in source directory |
| "Cover too small" | Use image at least 1400x2100 pixels |
| "Validation failed" | Check report for specific errors |
| "Broken images" | Verify image paths are relative to markdown files |
| "Encoding errors" | Files will be auto-converted to UTF-8 |

---

## Tips for Best Results

1. **Organize chapters** with numbered prefixes: `01-intro.md`, `02-chapter1.md`
2. **Use consistent heading levels**: Start each chapter with `# Title`
3. **Place images** in same directory as markdown or `images/` subfolder
4. **Add YAML frontmatter** for chapter metadata:
   ```yaml
   ---
   title: Chapter One
   ---
   ```
5. **Validate before publishing** with `epubcheck`
