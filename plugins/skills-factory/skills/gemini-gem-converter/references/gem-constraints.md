# Gemini Gems Constraints and Workarounds

Detailed platform constraints for converting Agent Skills to Gemini Gems.

## Contents

- [Constraint table](#constraint-table)
- [File limit strategies](#file-limit-strategies)
- [Script conversion](#script-conversion)
- [Asset handling](#asset-handling)
- [Naming conventions](#naming-conventions)
- [Quality degradation analysis](#quality-degradation-analysis)

## Constraint table

| Constraint | Impact | Workaround |
|------------|--------|------------|
| 10 file limit | Cannot include all references | Consolidate related files; prioritize core docs |
| No script execution | Cannot run automated tasks | Convert to instructional content |
| No API integration | Cannot call external services | Guide users to manual steps |
| No instruction char limit (unofficial) | Generally flexible | Test empirically; documentation sparse |
| Flat file structure | Loses organization | Use naming prefixes (REF_, SCRIPT_, ASSET_, WORKFLOW_) |
| No progressive disclosure | All knowledge files loaded equally | Front-load critical information in instructions |

## File limit strategies

With only 10 knowledge files available:

1. **Merge by domain** — Combine `finance.md`, `sales.md`, `marketing.md` into `REF_all_domains.md` with clear section headers
2. **Merge by type** — Combine all script conversions into a single `SCRIPT_all_procedures.md`
3. **Inline small references** — If a reference is under 500 words, include it directly in the instructions
4. **Prioritize by usage frequency** — Drop references that are rarely needed
5. **Target 5-7 files** — Leaves room for iteration and additions

### Consolidation example

**Before** (15 files, exceeds limit):
```
references/finance.md
references/sales.md
references/marketing.md
references/product.md
scripts/analyze.py
scripts/validate.py
scripts/export.py
assets/template.xlsx
assets/logo.png
references/api-v1.md
references/api-v2.md
references/migration.md
references/faq.md
references/glossary.md
references/changelog.md
```

**After** (7 files, within limit):
```
REF_domain_finance_sales.md          (finance + sales merged)
REF_domain_product_marketing.md      (product + marketing merged)
REF_api_reference.md                 (api-v1 + api-v2 + migration merged)
REF_support_faq_glossary.md          (faq + glossary merged)
SCRIPT_all_procedures.md             (analyze + validate + export converted)
ASSET_template.xlsx
ASSET_logo.png
```

## Script conversion

Since Gems cannot execute code, each script must become an instructional document.

### Conversion pattern

For each script file:

1. **Read the script** to understand its purpose, inputs, and outputs
2. **Write a "When to use" section** explaining the trigger conditions
3. **Extract the core logic** as a code snippet the user can copy/paste
4. **Add guidance steps** the AI can walk the user through
5. **Note dependencies** the user needs to install

### Example conversion

**Source** (`scripts/validate_form.py`):
```python
import json
import sys

def validate(fields_path):
    with open(fields_path) as f:
        fields = json.load(f)
    errors = []
    for name, config in fields.items():
        if 'value' not in config:
            errors.append(f"Missing value for field: {name}")
    return errors
```

**Target** (`SCRIPT_validate_form.md`):
```markdown
# Form Validation Procedure

## When to use
After creating a field mapping JSON, validate it before filling the form.

## Validation steps
1. Load the fields.json file
2. Check every field has a "value" key
3. Report any fields missing values

## Code for user
[Python snippet the user can run]

## Common issues
- Missing "value" key: Add the value for the listed field
- JSON parse error: Check for trailing commas or unquoted strings
```

## Asset handling

| Asset Type | Gem Strategy |
|------------|-------------|
| Templates (PPTX, DOCX) | Upload directly (counts toward 10-file limit) |
| Images (PNG, JPG) | Upload directly |
| Fonts (TTF, OTF) | Cannot upload — reference by name in instructions |
| Binary data | Upload if supported type |
| Large files (>100 MB) | Cannot upload — provide download instructions |

## Naming conventions

Use consistent prefixes for all knowledge files to preserve the organizational structure lost when flattening:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `REF_` | Reference documentation | `REF_api_reference.md` |
| `SCRIPT_` | Converted script logic | `SCRIPT_rotate_pdf.md` |
| `ASSET_` | Binary assets | `ASSET_template.pptx` |
| `WORKFLOW_` | Multi-step procedures | `WORKFLOW_deployment.md` |

### Flattening nested paths

Replace directory separators with underscores:
```
references/workflows/create.md  →  REF_workflows_create.md
scripts/utils/helpers.py        →  SCRIPT_utils_helpers.md
assets/templates/report.docx    →  ASSET_templates_report.docx
```

## Quality degradation analysis

### What gets lost in conversion

| Skill Feature | Loss Level | Mitigation |
|---------------|------------|------------|
| Script execution | High | Convert to instructional docs; user runs code locally |
| Progressive loading | Medium | Pre-consolidate important content into instructions |
| Directory hierarchy | Low | Naming convention preserves semantics |
| Unlimited references | Medium | Prioritize and consolidate to 10-file limit |
| Tool integrations | High | Guide users to manual alternatives |

### Capability retention by skill type

| Skill Type | Gem Retention |
|------------|---------------|
| Documentation/Knowledge | ~90% |
| Workflow guidance | ~80% |
| Code generation guidance | ~70% |
| Automated tasks | ~20% |
| External API integration | ~0% |

### Gem-specific opportunities

- **Google Drive integration**: Reference Google Docs/Sheets that auto-update for living documentation
- **Google ecosystem**: Built-in access to Google services
- **No instruction limit**: More flexible than GPTs for instruction length
