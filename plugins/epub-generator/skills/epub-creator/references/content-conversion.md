# Step 2: Content Conversion

## 2.1 Extract Metadata from Frontmatter

```python
import yaml
import re

def extract_frontmatter(content: str) -> tuple:
    """Extract YAML frontmatter and content."""
    frontmatter = {}

    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        try:
            frontmatter = yaml.safe_load(match.group(1))
            content = content[match.end():]
        except yaml.YAMLError:
            pass

    return frontmatter, content
```

## 2.2 Smart Title Extraction

```python
def extract_title(content: str, filename: str, frontmatter: dict) -> str:
    """Extract chapter title with fallback chain."""

    # 1. Check frontmatter
    if frontmatter.get('title'):
        return frontmatter['title']

    # 2. Find first heading
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()

    # 3. Fallback to filename
    name = Path(filename).stem
    # Remove leading numbers and dashes
    name = re.sub(r'^[\d\-_]+', '', name)
    return name.replace('-', ' ').replace('_', ' ').title()
```

## 2.3 Convert Markdown to XHTML

```python
import markdown
from bs4 import BeautifulSoup

def markdown_to_xhtml(content: str, title: str) -> str:
    """Convert markdown to valid EPUB XHTML."""

    # Use robust markdown extensions
    html = markdown.markdown(
        content,
        extensions=[
            'tables',
            'fenced_code',
            'toc',
            'smarty',       # Smart quotes and dashes
            'sane_lists',   # Better list handling
            'attr_list',    # HTML attributes
            'md_in_html',   # Markdown inside HTML blocks
        ],
        output_format='xhtml'
    )

    # Parse and clean with BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')

    # Ensure all images have alt text
    for img in soup.find_all('img'):
        if not img.get('alt'):
            img['alt'] = 'Image'

    # Add classes to first paragraphs after headings (no indent)
    for heading in soup.find_all(['h1', 'h2', 'h3']):
        next_p = heading.find_next_sibling('p')
        if next_p:
            next_p['class'] = next_p.get('class', []) + ['first']

    # Wrap in proper XHTML structure
    xhtml = f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
    <title>{title}</title>
    <link rel="stylesheet" type="text/css" href="../styles/main.css"/>
</head>
<body>
{soup.decode_contents()}
</body>
</html>'''

    return xhtml
```

## 2.4 Extract Nested ToC Structure

Generate hierarchical table of contents with section anchors:

```python
from slugify import slugify  # pip install python-slugify

def extract_toc_structure(content: str, chapter_file: str, toc_depth: int = 2) -> list:
    """Extract hierarchical TOC entries from chapter content.

    Args:
        content: HTML content of the chapter
        chapter_file: Filename for href links
        toc_depth: 1=H1 only, 2=H1+H2, 3=H1+H2+H3

    Returns:
        List of TOC entries with nested children
    """
    entries = []
    soup = BeautifulSoup(content, 'lxml')

    # Get H1 (chapter title)
    h1 = soup.find('h1')
    if h1:
        chapter_entry = {
            'title': h1.get_text().strip(),
            'href': chapter_file,
            'children': []
        }

        # Get H2 entries if toc_depth >= 2
        if toc_depth >= 2:
            for h2 in soup.find_all('h2'):
                h2_id = slugify(h2.get_text())
                h2['id'] = h2_id  # Add anchor to HTML
                h2_entry = {
                    'title': h2.get_text().strip(),
                    'href': f"{chapter_file}#{h2_id}",
                    'children': []
                }

                # Get H3 entries if toc_depth >= 3
                if toc_depth >= 3:
                    # Find H3s that follow this H2 (until next H2)
                    next_elem = h2.find_next_sibling()
                    while next_elem and next_elem.name != 'h2':
                        if next_elem.name == 'h3':
                            h3_id = slugify(next_elem.get_text())
                            next_elem['id'] = h3_id
                            h2_entry['children'].append({
                                'title': next_elem.get_text().strip(),
                                'href': f"{chapter_file}#{h3_id}"
                            })
                        next_elem = next_elem.find_next_sibling()

                chapter_entry['children'].append(h2_entry)

        entries.append(chapter_entry)

    return entries, str(soup)  # Return modified HTML with IDs


def build_nested_toc(toc_entries: list) -> tuple:
    """Build ebooklib TOC structure from nested entries."""
    toc = []

    for entry in toc_entries:
        if entry.get('children'):
            # Create section with children
            children = []
            for child in entry['children']:
                if child.get('children'):
                    # H2 with H3 children
                    grandchildren = [
                        epub.Link(gc['href'], gc['title'], gc['title'])
                        for gc in child['children']
                    ]
                    children.append((
                        epub.Link(child['href'], child['title'], child['title']),
                        grandchildren
                    ))
                else:
                    children.append(epub.Link(child['href'], child['title'], child['title']))

            toc.append((
                epub.Link(entry['href'], entry['title'], entry['title']),
                children
            ))
        else:
            toc.append(epub.Link(entry['href'], entry['title'], entry['title']))

    return toc
```
