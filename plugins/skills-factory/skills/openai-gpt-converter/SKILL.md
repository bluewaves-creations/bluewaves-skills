---
name: openai-gpt-converter
description: Convert Agent Skills to Custom GPT format. Use when the user wants to adapt, port, or transform a Claude skill (SKILL.md-based) into an OpenAI Custom GPT, or when discussing GPT constraints like the 8000-character instruction limit, knowledge file limits, Code Interpreter, Actions, and platform differences between Claude Skills and Custom GPTs.
allowed-tools: Bash, Read, Write
---

# OpenAI GPT Converter

Convert Agent Skills into Custom GPTs with awareness of platform constraints and optimal adaptation strategies.

## Platform Constraints Summary

| Aspect | Claude Skills | Custom GPTs |
|--------|---------------|-------------|
| **Instructions** | Unlimited (SKILL.md) | 8,000 characters |
| **Knowledge Files** | Unlimited | 20 files max |
| **File Size** | Varies by context | 512 MB per file |
| **File Structure** | Hierarchical | Flat |
| **Executable Scripts** | Yes (Python, Bash) | No (Code Interpreter only) |
| **API Integration** | Via scripts | Yes (Actions) |

For detailed constraints and workarounds, see [references/gpt-constraints.md](references/gpt-constraints.md).

## Conversion Workflow

### Step 1: Audit the Source Skill

Inventory all files in the source skill directory:

1. Read SKILL.md — note frontmatter fields, body length, and **character count**
2. List all files in `scripts/`, `references/`, and `assets/`
3. Count total files (GPTs allow max 20 knowledge files)
4. Identify scripts that could use Code Interpreter vs. needing conversion
5. Identify any API calls that could become GPT Actions

### Step 2: Condense SKILL.md for 8,000-Character Limit

This is the critical step. GPT instructions are limited to ~8,000 characters (~130 lines of markdown).

**Condensation strategies (in order of preference):**

1. **Extract to knowledge files** — Move detailed procedures, examples, and reference material into knowledge files. Keep only the core workflow and pointers in instructions.
2. **Remove Claude-specific syntax** — Strip file path references, tool invocation syntax, progressive disclosure directives.
3. **Compress verbose sections** — Replace multi-paragraph explanations with bullet points.
4. **Use reference pointers** — Replace inline content with `See [filename] for details`.
5. **Prioritize by importance** — Cut nice-to-have sections first.

**Character budget guidance:**

| Section | Suggested Budget |
|---------|-----------------|
| Role/purpose statement | ~500 chars |
| Core workflow steps | ~3,000 chars |
| Key rules and constraints | ~2,000 chars |
| Knowledge file pointers | ~1,500 chars |
| Edge cases and warnings | ~1,000 chars |

**Tiered importance for condensation:**

- **Must keep**: Core workflow, critical rules, safety constraints
- **Move to knowledge files**: Detailed examples, reference tables, alternative approaches
- **Can drop**: Explanatory context Claude already knows, redundant examples

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
- `ASSET_` — Binary assets
- `WORKFLOW_` — Multi-step procedures

Also create `REF_extended_instructions.md` for any instruction content that was moved out of the 8K character limit.

### Step 4: Evaluate Code Interpreter Opportunities

GPTs have Code Interpreter (a Python sandbox). For each script in the source skill:

| Script Characteristic | Recommendation |
|----------------------|----------------|
| Pure Python, no external deps | Good candidate for Code Interpreter |
| Requires pip packages | Check if available in Code Interpreter sandbox |
| Requires network access | Cannot use Code Interpreter — convert to instructions |
| Requires local file system | Cannot use Code Interpreter — convert to instructions |
| Simple data processing | Good candidate for Code Interpreter |

For Code Interpreter-compatible scripts, include them as knowledge files and instruct the GPT to execute them via Code Interpreter.

### Step 5: Evaluate Actions for API Integrations

If the source skill makes API calls via scripts, consider converting to GPT Actions:

1. **Identify API endpoints** used in the scripts
2. **Write OpenAPI spec** for each endpoint
3. **Configure authentication** in the GPT Actions settings
4. **Update instructions** to reference the Action instead of the script

Actions are appropriate when:
- The skill calls well-defined REST APIs
- Authentication can be configured (API key, OAuth)
- The API is publicly accessible

### Step 6: Consolidate to 20-File Limit

GPTs allow up to 20 knowledge files. If the source skill has more:

1. **Merge related references** into single files
2. **Prioritize core documentation**
3. **Inline short references** into instructions (within 8K limit)
4. **Aim for 10-15 files** to leave room for additions

**RAG considerations**: GPTs use retrieval (RAG) to find relevant knowledge file content. Structure files for chunk-friendly retrieval:
- Use clear section headers
- Front-load key information in each section
- Keep related content together (don't split a topic across files)
- Use descriptive file names that indicate content

### Step 7: Test the Custom GPT

1. Create the GPT in the GPT Builder with condensed instructions
2. Upload all knowledge files
3. Configure Code Interpreter and/or Actions if applicable
4. Test with representative queries from the original skill's use cases
5. Test in long conversations (GPTs can experience prompt drift)
6. Verify knowledge file retrieval works correctly
7. Iterate on instructions if the GPT misses important context

## Condensation Example

**Before** (2,500 characters, excerpt):
```markdown
## PDF Processing

### Overview
This skill provides comprehensive PDF processing capabilities including
text extraction, form filling, document merging, and page manipulation.
It uses pdfplumber for text extraction and pypdf for structural operations.

### Text Extraction
Use pdfplumber for text extraction. Install with pip install pdfplumber.
Then use the following code:
[20 lines of code]

### Form Filling
For form filling, first analyze the form with scripts/analyze_form.py...
```

**After** (800 characters):
```markdown
## PDF Processing

Extract text: `pdfplumber`. Fill forms: analyze → map → validate → fill.
Merge/split: `pypdf`.

See REF_pdf_procedures.md for code examples and detailed steps.
See SCRIPT_form_filling.md for form analysis workflow.
```

## Naming Convention Quick Reference

```
SKILL.md fields → GPT Configuration:
  name          → GPT Name
  description   → GPT Description
  body          → Instructions (max 8,000 chars)

Resource files → Knowledge Files:
  references/*  → REF_*.md
  scripts/*     → SCRIPT_*.md (or keep .py for Code Interpreter)
  assets/*      → ASSET_*
```

## Quality Expectations

| Skill Type | Expected GPT Retention |
|------------|----------------------|
| Documentation/Knowledge | ~95% |
| Workflow guidance | ~85% |
| Code generation guidance | ~80% |
| Automated tasks | ~50% (with Code Interpreter) |
| External API integration | ~70% (with Actions) |

GPTs retain more capability than Gems due to Code Interpreter and Actions. The main challenge is the 8,000-character instruction limit.
