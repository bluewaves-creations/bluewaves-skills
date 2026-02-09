---
name: gemini-gem-converter
description: Convert Agent Skills to Gemini Gems format. Use when the user wants to adapt, port, or transform a Claude skill (SKILL.md-based) into a Google Gemini Gem, or when discussing Gem constraints, knowledge file limits, and platform differences between Claude Skills and Gemini Gems.
allowed-tools: Bash, Read, Write
---

# Gemini Gem Converter

Convert Agent Skills into Gemini Gems with awareness of platform constraints and optimal adaptation strategies.

## Platform Constraints Summary

| Aspect | Claude Skills | Gemini Gems |
|--------|---------------|-------------|
| **Instructions** | Unlimited (SKILL.md) | No documented limit |
| **Knowledge Files** | Unlimited | 10 files max |
| **File Structure** | Hierarchical | Flat |
| **Executable Scripts** | Yes (Python, Bash) | No |
| **API Integration** | Via scripts | No |
| **Live Updates** | N/A | Yes (Google Docs/Sheets) |

For detailed constraints and workarounds, see [references/gem-constraints.md](references/gem-constraints.md).

## Conversion Workflow

### Step 1: Audit the Source Skill

Inventory all files in the source skill directory:

1. Read SKILL.md — note frontmatter fields and body length
2. List all files in `scripts/`, `references/`, and `assets/`
3. Count total files (Gems allow max 10 knowledge files)
4. Identify scripts that need conversion to instructional docs

### Step 2: Map SKILL.md to Gem Instructions

| Source | Target |
|--------|--------|
| YAML `name` | Gem Name |
| YAML `description` | First paragraph of Gem instructions |
| SKILL.md body | Full instructions field |

**Transformation rules:**

1. **Remove Claude-specific directives** — Strip file path references (`/mnt/skills/...`), remove tool invocation syntax, replace "Claude" with neutral terms ("this assistant")
2. **Adapt progressive disclosure** — Gems don't support lazy loading. Consolidate critical info into instructions. Use knowledge files for supplementary detail.
3. **Remove frontmatter** — Gems don't use YAML frontmatter. Extract name and description into the Gem configuration UI.

### Step 3: Convert Bundled Resources

Use this naming convention for the flat file structure:

```
Original:                           Derived:
references/api-docs.md         →    REF_api-docs.md
references/workflows/create.md →    REF_workflows_create.md
scripts/rotate_pdf.py          →    SCRIPT_rotate_pdf.md (converted)
assets/template.pptx           →    ASSET_template.pptx
```

**Prefix system:**
- `REF_` — Reference documentation
- `SCRIPT_` — Script logic (converted to readable format)
- `ASSET_` — Binary assets (images, templates)
- `WORKFLOW_` — Multi-step procedures

### Step 4: Convert Scripts to Instructional Documents

Since Gems cannot execute code, transform each script into:

1. **Procedural documentation** — Step-by-step instructions the AI can explain
2. **Code snippets for users** — Code the user can copy/paste and run locally
3. **Guidance on when to use** — Context for when this procedure applies

Example transformation:

**Source** (`scripts/rotate_pdf.py`):
```python
def rotate_pdf(input_path, degrees):
    from pypdf import PdfReader, PdfWriter
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reader.pages:
        page.rotate(degrees)
        writer.add_page(page)
    return writer
```

**Target** (`SCRIPT_rotate_pdf.md`):
```markdown
# PDF Rotation Procedure

## When to use
User wants to rotate pages in a PDF document.

## Steps to guide user
1. Explain that PDF rotation requires a Python environment
2. Provide this code for the user to run:
   [Python code snippet]
3. Offer to explain any part of the code
4. Suggest online alternatives if user cannot run Python
```

### Step 5: Consolidate to 10-File Limit

Gems allow a maximum of 10 knowledge files. If the source skill has more than 10 resource files:

1. **Merge related references** into single files (e.g., combine all API docs)
2. **Prioritize core documentation** — drop files that are nice-to-have
3. **Inline short references** into the instructions field
4. **Aim for 5-7 files** to leave room for future additions

### Step 6: Test the Gem

1. Create the Gem in Google AI Studio with the converted instructions
2. Upload all knowledge files
3. Test with representative queries from the original skill's use cases
4. Verify the Gem finds and uses knowledge files correctly
5. Iterate on instructions if the Gem misses important context

## Platform Opportunities

**Google Drive integration**: Gems can reference Google Docs/Sheets that auto-update. For skills with frequently changing reference data, consider linking a Google Sheet instead of a static knowledge file.

## Naming Convention Quick Reference

```
SKILL.md fields → Gem Configuration:
  name          → Gem Name
  description   → Instructions (first paragraph)
  body          → Instructions (full content)

Resource files → Knowledge Files:
  references/*  → REF_*.md
  scripts/*     → SCRIPT_*.md (converted from code to docs)
  assets/*      → ASSET_* (uploaded directly if supported type)
```

## Quality Expectations

| Skill Type | Expected Gem Retention |
|------------|----------------------|
| Documentation/Knowledge | ~90% |
| Workflow guidance | ~80% |
| Code generation guidance | ~70% |
| Automated tasks (scripts) | ~20% |
| External API integration | ~0% |

Script-heavy skills will lose the most capability. Knowledge-heavy skills translate well.
