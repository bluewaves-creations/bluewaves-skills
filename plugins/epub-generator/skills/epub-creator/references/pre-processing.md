# Step 1: Pre-Processing (Input Validation & Fixes)

Before conversion, validate and fix all inputs.

## 1.1 Gather Inputs

```python
from pathlib import Path
import re

def gather_inputs(source_dir: str):
    """Collect and validate all input files."""
    source = Path(source_dir)

    inputs = {
        'markdown_files': sorted(source.glob('**/*.md')),
        'images': list(source.glob('**/*.{jpg,jpeg,png,gif,svg}')),
        'cover': None,
        'metadata': {}
    }

    # Find cover image
    for pattern in ['cover.*', 'Cover.*', '*cover*.*']:
        covers = list(source.glob(pattern))
        if covers:
            inputs['cover'] = covers[0]
            break

    # Look for metadata file
    meta_file = source / 'metadata.yaml'
    if meta_file.exists():
        import yaml
        with open(meta_file) as f:
            inputs['metadata'] = yaml.safe_load(f)

    return inputs
```

## 1.2 Fix Markdown Quirks

```python
def fix_markdown_quirks(content: str) -> str:
    """Fix common markdown issues."""

    # Normalize line endings
    content = content.replace('\r\n', '\n').replace('\r', '\n')

    # Fix inconsistent heading levels (ensure starts with #)
    lines = content.split('\n')
    fixed_lines = []
    found_first_heading = False

    for line in lines:
        # Detect heading
        if line.startswith('#'):
            if not found_first_heading:
                # Ensure first heading is h1
                heading_match = re.match(r'^(#+)\s*(.+)$', line)
                if heading_match:
                    level = len(heading_match.group(1))
                    if level > 1:
                        line = f'# {heading_match.group(2)}'
                found_first_heading = True
        fixed_lines.append(line)

    content = '\n'.join(fixed_lines)

    # Fix unclosed emphasis
    # Count asterisks and underscores, close if odd
    for char in ['*', '_']:
        count = content.count(char)
        if count % 2 == 1:
            content += char

    # Ensure blank line before headings
    content = re.sub(r'([^\n])\n(#{1,6}\s)', r'\1\n\n\2', content)

    # Fix broken links - remove if target missing
    content = re.sub(r'\[([^\]]+)\]\(\s*\)', r'\1', content)

    # Normalize whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)

    return content.strip() + '\n'
```

## 1.3 Validate Images

```python
from PIL import Image
import os

def validate_and_fix_images(image_paths: list, max_size_mb: float = 2.0):
    """Validate images and optimize if needed."""
    validated = []
    issues = []

    for img_path in image_paths:
        path = Path(img_path)

        try:
            with Image.open(path) as img:
                # Check format
                if img.format not in ['JPEG', 'PNG', 'GIF']:
                    issues.append(f"Converting {path.name} to PNG")
                    new_path = path.with_suffix('.png')
                    img.save(new_path, 'PNG')
                    path = new_path

                # Check size
                size_mb = os.path.getsize(path) / (1024 * 1024)
                if size_mb > max_size_mb:
                    issues.append(f"Optimizing {path.name} ({size_mb:.1f}MB)")
                    # Resize large images
                    if max(img.size) > 2000:
                        ratio = 2000 / max(img.size)
                        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                    img.save(path, optimize=True, quality=85)

                validated.append({
                    'path': path,
                    'size': img.size,
                    'format': img.format
                })

        except Exception as e:
            issues.append(f"ERROR: Cannot read {path.name}: {e}")

    return validated, issues
```

## 1.4 Validate Cover Image

```python
def validate_cover(cover_path: str) -> tuple:
    """Ensure cover meets EPUB requirements."""
    RECOMMENDED_SIZE = (1600, 2400)
    MIN_SIZE = (1400, 2100)

    issues = []

    with Image.open(cover_path) as img:
        width, height = img.size

        # Check minimum size
        if width < MIN_SIZE[0] or height < MIN_SIZE[1]:
            issues.append(f"Cover too small ({width}x{height}), minimum {MIN_SIZE[0]}x{MIN_SIZE[1]}")

        # Check aspect ratio (should be ~1:1.5)
        ratio = height / width
        if ratio < 1.3 or ratio > 1.7:
            issues.append(f"Cover aspect ratio {ratio:.2f} not ideal (should be ~1.5)")

        # Convert to RGB if needed (remove alpha)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
            cover_path = Path(cover_path).with_suffix('.jpg')
            img.save(cover_path, 'JPEG', quality=95)
            issues.append(f"Converted cover to JPEG")

    return cover_path, issues
```

## 1.5 Pre-Validate All Sources

Run comprehensive validation before processing:

```python
def validate_sources(source_dir: str) -> dict:
    """Pre-validate all source files before processing."""
    report = {
        'valid': True,
        'markdown_files': [],
        'images': [],
        'errors': [],
        'warnings': []
    }

    source = Path(source_dir)

    # Check directory exists
    if not source.exists():
        report['valid'] = False
        report['errors'].append(f"Source directory not found: {source_dir}")
        return report

    # Find markdown files
    md_files = sorted(source.glob('*.md'))
    if not md_files:
        md_files = sorted(source.glob('**/*.md'))

    if not md_files:
        report['valid'] = False
        report['errors'].append("No markdown files found")
        return report

    print(f"Pre-validating {len(md_files)} markdown files...")

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
            report['markdown_files'].append({
                'path': str(md_file),
                'size': md_file.stat().st_size,
                'word_count': len(content.split())
            })

            # Check for broken image references
            img_refs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
            for alt, img_path in img_refs:
                full_path = (md_file.parent / img_path).resolve()
                if not full_path.exists():
                    report['warnings'].append(f"Missing image: {img_path} in {md_file.name}")
                else:
                    report['images'].append(str(full_path))

        except Exception as e:
            report['errors'].append(f"Cannot read {md_file.name}: {e}")

    # Check for cover
    cover_patterns = ['cover.jpg', 'cover.png', 'Cover.jpg', 'Cover.png']
    cover_found = any((source / p).exists() for p in cover_patterns)
    if not cover_found:
        report['warnings'].append("No cover image found (optional but recommended)")

    report['valid'] = len(report['errors']) == 0

    # Print summary
    print(f"   {len(report['markdown_files'])} markdown files")
    print(f"   {len(report['images'])} images referenced")
    if report['warnings']:
        for w in report['warnings']:
            print(f"   WARNING: {w}")
    if report['errors']:
        for e in report['errors']:
            print(f"   ERROR: {e}")

    return report
```
