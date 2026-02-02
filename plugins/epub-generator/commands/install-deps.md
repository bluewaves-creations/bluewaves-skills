---
description: Install Python dependencies required by the epub-creator skill
---
Install all Python packages needed by the epub-creator skill and verify they work.

$ARGUMENTS

If `--pip` is passed as an argument, use `pip install` instead of `uv pip install`.

## Steps

1. **Determine installer:** Use `uv pip install` by default. If `$ARGUMENTS` contains `--pip`, use `pip install` instead.

2. **Install dependencies:**
   ```bash
   uv pip install ebooklib markdown Pillow beautifulsoup4 lxml PyYAML
   ```

3. **Verify imports:**
   ```bash
   python3 -c "
   import ebooklib
   import markdown
   from PIL import Image
   from bs4 import BeautifulSoup
   import lxml
   import yaml
   print('All 6 dependencies verified successfully.')
   "
   ```

4. **Check for optional epubcheck:**
   ```bash
   if command -v epubcheck &>/dev/null; then
     echo "epubcheck is available: $(epubcheck --version 2>&1 | head -1)"
   else
     echo "Optional: epubcheck not found. Install via 'brew install epubcheck' for EPUB validation."
   fi
   ```

5. **Report results** with a summary of what was installed and verified.
