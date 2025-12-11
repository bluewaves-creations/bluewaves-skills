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

```bash
uv pip install ebooklib markdown
```

Optional for validation:
```bash
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

- Markdown to EPUB conversion
- Cover image embedding
- Automatic table of contents
- CSS styling
- Image embedding
- EPUB 3 validation support

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

## License

MIT
