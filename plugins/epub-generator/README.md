# epub-generator Plugin

Generate validated EPUB 3 ebooks from markdown files and images.

## Installation

```bash
# Add the Bluewaves marketplace
/plugin marketplace add bluewaves-creations/bluewaves-skills

# Install this plugin
/plugin install epub-generator@bluewaves-skills
```

## Prerequisites

**Python Version**: Requires Python 3.8 or higher

```bash
# Install all required packages (using uv)
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

## Skills Included

| Skill | Description |
|-------|-------------|
| **epub-creator** | Generate EPUB from markdown files with cover images and TOC |

## Usage Examples

### Create an EPUB from markdown files
> "Create an EPUB book from the markdown files in ./chapters with cover.jpg as the cover"

### Convert a single markdown file
> "Convert this markdown file to an EPUB ebook"

### Generate with metadata
> "Create an EPUB titled 'My Book' by 'John Doe' from these markdown files"

## Features

- **Markdown to EPUB conversion** with smart formatting fixes
- **Cover image embedding** with automatic optimization
- **Hierarchical table of contents** (nested H1/H2/H3 support)
- **Professional CSS styling** with typography best practices
- **Image optimization** with automatic resizing for large files
- **Pre-validation** of source files before processing
- **Post-validation** with comprehensive EPUB checks
- **Progress reporting** during generation
- **Dependency validation** hook to catch missing packages

## Project Structure

Recommended structure for your book project:

```
my-book/
├── chapters/
│   ├── 01-introduction.md
│   ├── 02-chapter-one.md
│   └── 03-conclusion.md
├── images/
│   ├── cover.jpg
│   └── illustrations/
└── output/
    └── my-book.epub
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "No module named 'ebooklib'" | Run `pip install ebooklib markdown Pillow beautifulsoup4 lxml PyYAML` |
| "No markdown files found" | Ensure `.md` files exist in source directory |
| "Cover too small" | Use cover image at least 1400x2100 pixels |
| "EPUB validation failed" | Check the generated report for specific errors |
| "Broken images" | Verify image paths are relative to markdown files |
| "Encoding errors" | Files with encoding issues are auto-converted to UTF-8 |

### Verifying Your Setup

```bash
# Check Python version (requires 3.8+)
python3 --version

# Verify all packages are installed
python3 -c "import ebooklib, markdown, PIL, bs4, lxml, yaml; print('All packages OK')"

# Test epubcheck (optional)
epubcheck --version
```

### Tips for Best Results

1. **Organize chapters** with numbered prefixes: `01-intro.md`, `02-chapter1.md`
2. **Use consistent heading levels**: Start each chapter with `# Title`
3. **Place images** in same directory as markdown or `images/` subfolder
4. **Use high-quality cover**: At least 1400x2100 pixels, 1:1.5 aspect ratio
5. **Add YAML frontmatter** for chapter metadata if needed

## License

MIT
