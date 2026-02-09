---
description: Generate a branded PDF document from a markdown file
---
Generate a production-grade branded PDF from a markdown source file using the pdf-factory pipeline.

$ARGUMENTS

Parse arguments: `<markdown-file> [--brand <name>] [--output <path>]`

- `<markdown-file>` — path to the source markdown file (required)
- `--brand <name>` — brand kit name: `bluewaves`, `wave-artisans`, or `decathlon` (default: `bluewaves`)
- `--output <path>` — output PDF path (default: same directory as input, `.pdf` extension)

## Steps

1. **Parse arguments** from `$ARGUMENTS`. Extract markdown file path, brand name, and output path.

2. **Verify dependencies** are installed:
   ```bash
   python3 -c "import xhtml2pdf, reportlab, pypdf, markdown, lxml, PIL, html5lib, cssselect2" 2>/dev/null
   ```
   If this fails, run `/docs-factory:install-deps` first.

3. **Resolve brand kit** at `${CLAUDE_PLUGIN_ROOT}/skills/brand-<name>/`. Verify the directory exists and contains `assets/manifest.json`.

4. **Read the markdown file** and extract frontmatter metadata (title, subtitle, author, date). Convert markdown to HTML:
   ```bash
   python3 -c "
   import markdown, json, sys, re
   with open('<markdown-file>') as f:
       source = f.read()
   # Extract YAML frontmatter
   fm_match = re.match(r'^---\n(.*?)\n---\n', source, re.DOTALL)
   meta = {}
   if fm_match:
       for line in fm_match.group(1).splitlines():
           if ':' in line:
               key, val = line.split(':', 1)
               meta[key.strip()] = val.strip()
       source = source[fm_match.end():]
   # Convert to HTML
   html = markdown.markdown(source, extensions=['tables', 'fenced_code', 'codehilite', 'toc', 'meta', 'attr_list'])
   with open('<output-dir>/content.html', 'w') as f:
       f.write(html)
   with open('<output-dir>/metadata.json', 'w') as f:
       json.dump(meta, f, indent=2)
   print('Parsed markdown and extracted metadata.')
   "
   ```

5. **Render content pages:**
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/pdf-factory/scripts/render.py \
     --brand ${CLAUDE_PLUGIN_ROOT}/skills/brand-<name> \
     --input <output-dir>/content.html \
     --output <output-dir>/content-pages.pdf
   ```

6. **Compose final document:**
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/pdf-factory/scripts/compose.py \
     --brand ${CLAUDE_PLUGIN_ROOT}/skills/brand-<name> \
     --content <output-dir>/content-pages.pdf \
     --metadata <output-dir>/metadata.json \
     --output <output-path>
   ```

7. **Validate output:**
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/pdf-factory/scripts/validate_output.py \
     <output-path> \
     --brand ${CLAUDE_PLUGIN_ROOT}/skills/brand-<name>
   ```

8. **Clean up** temporary files (content.html, content-pages.pdf, metadata.json).

9. **Report results** — output path, page count, file size, and validation status.
