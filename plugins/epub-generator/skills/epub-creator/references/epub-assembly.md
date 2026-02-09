# Step 3: EPUB Assembly

## 3.1 Professional CSS Stylesheet

```python
EPUB_CSS = '''
/* Professional EPUB Stylesheet */
@charset "UTF-8";

/* Base Typography */
body {
    font-family: Georgia, "Times New Roman", serif;
    font-size: 1em;
    line-height: 1.6;
    margin: 1em;
    text-align: justify;
    hyphens: auto;
    -webkit-hyphens: auto;
}

/* Headings */
h1 {
    font-size: 1.8em;
    font-weight: bold;
    margin: 2em 0 1em;
    text-align: center;
    page-break-before: always;
    page-break-after: avoid;
}

h2 {
    font-size: 1.4em;
    font-weight: bold;
    margin: 1.5em 0 0.5em;
    page-break-after: avoid;
}

h3 {
    font-size: 1.2em;
    font-weight: bold;
    margin: 1em 0 0.5em;
}

/* Paragraphs */
p {
    margin: 0.5em 0;
    text-indent: 1.5em;
}

p.first,
h1 + p,
h2 + p,
h3 + p,
blockquote + p {
    text-indent: 0;
}

/* Block Elements */
blockquote {
    margin: 1em 2em;
    font-style: italic;
    border-left: 3px solid #ccc;
    padding-left: 1em;
}

/* Code */
code {
    font-family: "Courier New", Courier, monospace;
    font-size: 0.9em;
    background-color: #f5f5f5;
    padding: 0.1em 0.3em;
    border-radius: 3px;
}

pre {
    font-family: "Courier New", Courier, monospace;
    font-size: 0.85em;
    background-color: #f5f5f5;
    padding: 1em;
    margin: 1em 0;
    overflow-x: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
    border-radius: 5px;
}

pre code {
    background: none;
    padding: 0;
}

/* Lists */
ul, ol {
    margin: 0.5em 0 0.5em 2em;
    padding: 0;
}

li {
    margin: 0.3em 0;
}

/* Images */
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1em auto;
}

figure {
    margin: 1em 0;
    text-align: center;
}

figcaption {
    font-size: 0.9em;
    font-style: italic;
    color: #666;
    margin-top: 0.5em;
}

/* Tables */
table {
    border-collapse: collapse;
    margin: 1em auto;
    font-size: 0.9em;
}

th, td {
    border: 1px solid #ccc;
    padding: 0.5em;
    text-align: left;
}

th {
    background-color: #f5f5f5;
    font-weight: bold;
}

/* Links */
a {
    color: #0066cc;
    text-decoration: none;
}

/* Horizontal Rule */
hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 2em 0;
}
'''
```

## 3.2 Complete EPUB Builder

```python
from ebooklib import epub
from pathlib import Path
import uuid
from datetime import datetime

def create_production_epub(
    source_dir: str,
    output_path: str,
    title: str,
    author: str,
    language: str = 'en',
    cover_path: str = None,
    publisher: str = None,
    description: str = None,
    # Configurable parameters
    max_image_size_mb: float = 2.0,
    max_image_dimension: int = 2000,
    image_quality: int = 85,
    cover_min_width: int = 1400,
    cover_min_height: int = 2100,
    toc_depth: int = 2,  # 1=chapters only, 2=include H2, 3=include H3
    custom_css: str = None,
) -> dict:
    """Create a production-quality EPUB with full QA.

    Args:
        source_dir: Directory containing markdown files
        output_path: Output EPUB file path
        title: Book title
        author: Author name
        language: Language code (default: 'en')
        cover_path: Path to cover image (optional)
        publisher: Publisher name (optional)
        description: Book description (optional)
        max_image_size_mb: Maximum image file size before optimization
        max_image_dimension: Maximum image dimension in pixels
        image_quality: JPEG quality for optimized images (1-100)
        cover_min_width: Minimum cover width in pixels
        cover_min_height: Minimum cover height in pixels
        toc_depth: Table of contents depth (1-3)
        custom_css: Custom CSS to append to stylesheet

    Returns:
        dict: Creation report with status, chapters, fixes, and errors
    """

    print(f"Starting EPUB creation: {title}")
    print(f"   Source: {source_dir}")
    print(f"   Output: {output_path}")

    report = {
        'status': 'success',
        'fixes_applied': [],
        'warnings': [],
        'errors': [],
        'chapters': [],
        'images': []
    }

    # Initialize book
    book = epub.EpubBook()
    book.set_identifier(str(uuid.uuid4()))
    book.set_title(title)
    book.set_language(language)
    book.add_author(author)

    if publisher:
        book.add_metadata('DC', 'publisher', publisher)
    if description:
        book.add_metadata('DC', 'description', description)

    book.add_metadata('DC', 'date', datetime.now().strftime('%Y-%m-%d'))

    # Add CSS
    css = epub.EpubItem(
        uid='main_css',
        file_name='styles/main.css',
        media_type='text/css',
        content=EPUB_CSS
    )
    book.add_item(css)

    # Process cover
    if cover_path and Path(cover_path).exists():
        cover_path, cover_issues = validate_cover(cover_path)
        report['fixes_applied'].extend(cover_issues)

        with open(cover_path, 'rb') as f:
            book.set_cover('images/cover.jpg', f.read())

    # Gather and process markdown files
    source = Path(source_dir)
    md_files = sorted(source.glob('**/*.md'))

    if not md_files:
        report['errors'].append('No markdown files found')
        report['status'] = 'failed'
        return report

    chapters = []
    toc = []
    image_items = {}

    print(f"   Processing {len(md_files)} chapters...")

    for i, md_file in enumerate(md_files, 1):
        print(f"      [{i}/{len(md_files)}] {md_file.name}")

        # Read and fix content
        with open(md_file, 'r', encoding='utf-8', errors='replace') as f:
            raw_content = f.read()

        # Extract frontmatter
        frontmatter, content = extract_frontmatter(raw_content)

        # Fix quirks
        original_content = content
        content = fix_markdown_quirks(content)
        if content != original_content:
            report['fixes_applied'].append(f'Fixed markdown quirks in {md_file.name}')

        # Extract title
        chapter_title = extract_title(content, md_file.name, frontmatter)

        # Find and process images referenced in this chapter
        img_refs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
        for alt, img_path in img_refs:
            img_full_path = (md_file.parent / img_path).resolve()
            if img_full_path.exists() and str(img_full_path) not in image_items:
                with open(img_full_path, 'rb') as f:
                    img_content = f.read()

                img_name = f'images/{img_full_path.name}'
                img_item = epub.EpubImage()
                img_item.file_name = img_name
                img_item.content = img_content
                book.add_item(img_item)
                image_items[str(img_full_path)] = img_name
                report['images'].append(img_full_path.name)

            # Update path in content
            if str(img_full_path) in image_items:
                content = content.replace(f']({img_path})', f'](../{image_items[str(img_full_path)]})')

        # Convert to XHTML
        xhtml = markdown_to_xhtml(content, chapter_title)

        # Create chapter
        chapter = epub.EpubHtml(
            title=chapter_title,
            file_name=f'chapters/chapter_{i:02d}.xhtml',
            lang=language
        )
        chapter.content = xhtml
        chapter.add_item(css)

        book.add_item(chapter)
        chapters.append(chapter)
        toc.append(epub.Link(f'chapters/chapter_{i:02d}.xhtml', chapter_title, f'ch{i}'))

        report['chapters'].append({
            'file': md_file.name,
            'title': chapter_title,
            'word_count': len(content.split())
        })

    # Build TOC and spine
    book.toc = toc
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ['nav'] + chapters

    # Write EPUB
    print(f"   Assembling EPUB...")
    epub.write_epub(output_path, book, {})

    print(f"   Created: {output_path}")
    report['output'] = output_path
    report['total_chapters'] = len(chapters)
    report['total_images'] = len(image_items)

    return report
```
