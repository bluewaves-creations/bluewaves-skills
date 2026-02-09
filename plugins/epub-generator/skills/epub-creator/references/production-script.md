# Step 5: Complete Production Script

```python
#!/usr/bin/env python3
"""
Production EPUB Creator
Creates validated, publication-ready EPUB files from markdown.
"""

from pathlib import Path
import json
from datetime import datetime

def create_epub_production(
    source_dir: str,
    output_dir: str = None,
    title: str = None,
    author: str = 'Unknown Author',
    **kwargs
) -> str:
    """
    Create a production-quality EPUB with full QA.

    Args:
        source_dir: Directory containing markdown files and images
        output_dir: Output directory (default: source_dir)
        title: Book title (default: derived from directory name)
        author: Author name
        **kwargs: Additional metadata (language, publisher, description)

    Returns:
        Path to created EPUB file
    """
    source = Path(source_dir)
    output_dir = Path(output_dir or source_dir)

    # Default title from directory name
    if not title:
        title = source.name.replace('-', ' ').replace('_', ' ').title()

    # Create output filename
    safe_title = "".join(c if c.isalnum() or c in ' -_' else '' for c in title)
    output_path = output_dir / f'{safe_title.replace(" ", "_")}.epub'

    print(f"Creating EPUB: {title}")
    print(f"Source: {source}")
    print(f"Output: {output_path}")
    print("-" * 50)

    # Find cover
    cover_path = None
    for pattern in ['cover.jpg', 'cover.png', 'Cover.*', '*cover*.*']:
        covers = list(source.glob(pattern))
        if covers:
            cover_path = str(covers[0])
            break

    # Create EPUB
    report = create_production_epub(
        source_dir=str(source),
        output_path=str(output_path),
        title=title,
        author=author,
        cover_path=cover_path,
        **kwargs
    )

    # Run QA
    qa = qa_checklist(str(output_path), report)

    # Print report
    print(f"\nEPUB Creation Report")
    print("=" * 50)
    print(f"Title: {title}")
    print(f"Author: {author}")
    print(f"Chapters: {report.get('total_chapters', 0)}")
    print(f"Images: {report.get('total_images', 0)}")

    if report.get('fixes_applied'):
        print(f"\nFixes Applied ({len(report['fixes_applied'])}):")
        for fix in report['fixes_applied']:
            print(f"  - {fix}")

    print(f"\nQA Status: {qa['status']}")
    for item in qa['passed']:
        print(f"  PASS: {item}")
    for item in qa['failed']:
        print(f"  FAIL: {item}")
    for item in qa['warnings']:
        print(f"  WARN: {item}")

    # Save report
    report_path = output_path.with_suffix('.report.json')
    with open(report_path, 'w') as f:
        json.dump({
            'creation_report': report,
            'qa_report': qa,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2, default=str)

    print(f"\nReport saved: {report_path}")
    print(f"EPUB created: {output_path}")

    return str(output_path)


# Usage
if __name__ == '__main__':
    create_epub_production(
        source_dir='./my-book',
        title='My Amazing Book',
        author='John Doe',
        language='en',
        publisher='Self Published',
        description='A wonderful book about...'
    )
```
