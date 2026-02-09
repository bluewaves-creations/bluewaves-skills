# Step 4: Validation & QA

## 4.1 EPUB Validation

```python
import subprocess
import zipfile

def validate_epub(epub_path: str) -> dict:
    """Validate EPUB with epubcheck."""
    result = {
        'valid': False,
        'errors': [],
        'warnings': []
    }

    try:
        # Try Python epubcheck wrapper
        output = subprocess.run(
            ['python', '-m', 'epubcheck', epub_path],
            capture_output=True,
            text=True
        )

        if output.returncode == 0:
            result['valid'] = True
        else:
            # Parse errors from output
            for line in output.stderr.split('\n'):
                if 'ERROR' in line:
                    result['errors'].append(line)
                elif 'WARNING' in line:
                    result['warnings'].append(line)

    except FileNotFoundError:
        # Fallback: basic structure validation
        result['warnings'].append('epubcheck not installed, using basic validation')

        with zipfile.ZipFile(epub_path, 'r') as zf:
            files = zf.namelist()

            # Check required files
            required = ['mimetype', 'META-INF/container.xml']
            for req in required:
                if req not in files:
                    result['errors'].append(f'Missing required file: {req}')

            # Check mimetype content
            mimetype = zf.read('mimetype').decode('utf-8')
            if mimetype != 'application/epub+zip':
                result['errors'].append('Invalid mimetype')

            if not result['errors']:
                result['valid'] = True

    return result
```

## 4.2 Comprehensive Post-Validation

Run thorough checks on the generated EPUB:

```python
import zipfile
import subprocess

def post_validate_epub(epub_path: str) -> dict:
    """Comprehensive post-creation validation."""
    report = {
        'valid': True,
        'checks': [],
        'errors': [],
        'warnings': []
    }

    path = Path(epub_path)

    print(f"\nPost-validating: {path.name}")

    # 1. File exists and readable
    if not path.exists():
        report['valid'] = False
        report['errors'].append("EPUB file not created")
        return report
    report['checks'].append("File exists")

    # 2. File size check
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > 50:
        report['warnings'].append(f"Large file: {size_mb:.1f}MB (may cause reader issues)")
    elif size_mb < 0.001:
        report['valid'] = False
        report['errors'].append("File too small - likely empty or corrupted")
    report['checks'].append(f"File size: {size_mb:.2f}MB")

    # 3. Valid ZIP structure
    try:
        with zipfile.ZipFile(path, 'r') as zf:
            names = zf.namelist()

            # Check mimetype
            if 'mimetype' not in names:
                report['errors'].append("Missing mimetype file")
                report['valid'] = False
            else:
                mime = zf.read('mimetype').decode('utf-8')
                if mime.strip() != 'application/epub+zip':
                    report['errors'].append(f"Invalid mimetype: {mime}")
                    report['valid'] = False
                else:
                    report['checks'].append("Valid mimetype")

            # Check container.xml
            if 'META-INF/container.xml' not in names:
                report['errors'].append("Missing container.xml")
                report['valid'] = False
            else:
                report['checks'].append("Container.xml present")

            # Check for content
            xhtml_files = [n for n in names if n.endswith('.xhtml')]
            if not xhtml_files:
                report['errors'].append("No XHTML content files")
                report['valid'] = False
            else:
                report['checks'].append(f"{len(xhtml_files)} content files")

            # Check for styles
            css_files = [n for n in names if n.endswith('.css')]
            if css_files:
                report['checks'].append(f"{len(css_files)} stylesheet(s)")

            # Check for images
            img_files = [n for n in names if any(n.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif'])]
            if img_files:
                report['checks'].append(f"{len(img_files)} image(s)")

    except zipfile.BadZipFile:
        report['valid'] = False
        report['errors'].append("Invalid ZIP/EPUB structure")

    # 4. Try epubcheck if available
    try:
        result = subprocess.run(
            ['epubcheck', str(path)],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            report['checks'].append("epubcheck validation passed")
        else:
            # Parse epubcheck output for specific issues
            for line in result.stderr.split('\n'):
                if 'ERROR' in line:
                    report['errors'].append(line.strip())
                elif 'WARNING' in line:
                    report['warnings'].append(line.strip())
    except FileNotFoundError:
        report['checks'].append("epubcheck not installed (optional)")
    except subprocess.TimeoutExpired:
        report['warnings'].append("epubcheck timed out - file may be too large")

    # Print summary
    for check in report['checks']:
        print(f"   {check}")
    for warning in report['warnings']:
        print(f"   WARNING: {warning}")
    for error in report['errors']:
        print(f"   ERROR: {error}")

    return report
```

## 4.3 Content QA Checklist

```python
def qa_checklist(epub_path: str, report: dict) -> dict:
    """Run QA checklist on generated EPUB."""
    qa = {
        'passed': [],
        'failed': [],
        'warnings': []
    }

    # 1. Check file exists and size
    path = Path(epub_path)
    if path.exists():
        qa['passed'].append(f'EPUB created: {path.name}')
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > 50:
            qa['warnings'].append(f'Large file size: {size_mb:.1f}MB')
    else:
        qa['failed'].append('EPUB file not created')
        return qa

    # 2. Check chapter count
    if report.get('total_chapters', 0) > 0:
        qa['passed'].append(f'Chapters: {report["total_chapters"]}')
    else:
        qa['failed'].append('No chapters in EPUB')

    # 3. Check for fixes applied
    if report.get('fixes_applied'):
        qa['warnings'].append(f'Fixes applied: {len(report["fixes_applied"])}')

    # 4. Validate structure
    validation = validate_epub(epub_path)
    if validation['valid']:
        qa['passed'].append('EPUB validation: PASSED')
    else:
        qa['failed'].append('EPUB validation: FAILED')
        qa['failed'].extend(validation['errors'])

    qa['warnings'].extend(validation.get('warnings', []))

    # 5. Overall status
    qa['status'] = 'PASSED' if not qa['failed'] else 'FAILED'

    return qa
```
