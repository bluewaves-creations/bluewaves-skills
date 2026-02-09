---
description: Install Python dependencies required by the pdf-factory skill
---
Install all Python packages needed by the pdf-factory skill and verify they work.

$ARGUMENTS

If `--pip` is passed as an argument, use `pip install --break-system-packages` instead of the default installer.

## Steps

1. **Run installer script:**
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/pdf-factory/scripts/install_deps.py
   ```

2. **Verify imports:**
   ```bash
   python3 -c "
   import xhtml2pdf
   import reportlab
   import pypdf
   import markdown
   import lxml
   from PIL import Image
   import html5lib
   import cssselect2
   print('All 9 core dependencies verified successfully.')
   "
   ```

3. **Check optional packages:**
   ```bash
   python3 -c "
   try:
       import pyhanko
       print('pyhanko (PDF signing): available')
   except ImportError:
       print('pyhanko (PDF signing): not available (optional)')
   try:
       import bidi
       print('python-bidi (RTL text): available')
   except ImportError:
       print('python-bidi (RTL text): not available (optional)')
   "
   ```

4. **Report results** with a summary of what was installed and verified.
