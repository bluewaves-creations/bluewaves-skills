# Custom GPT Constraints and Workarounds

Detailed platform constraints for converting Agent Skills to OpenAI Custom GPTs.

## Contents

- [Constraint table](#constraint-table)
- [8,000-character instruction limit](#8000-character-instruction-limit)
- [Code Interpreter](#code-interpreter)
- [Actions for API integration](#actions-for-api-integration)
- [Knowledge file retrieval (RAG)](#knowledge-file-retrieval-rag)
- [Asset handling](#asset-handling)
- [Naming conventions](#naming-conventions)
- [Quality degradation analysis](#quality-degradation-analysis)

## Constraint table

| Constraint | Impact | Workaround |
|------------|--------|------------|
| 8,000 char instruction limit | Forces extreme condensation of SKILL.md | Move details to knowledge files |
| 20 file limit | Better than Gems but still limited | Consolidate aggressively if needed |
| No native script execution | Cannot automate directly | Use Code Interpreter capability |
| RAG via embeddings | May miss context in knowledge files | Structure files for chunk-friendly retrieval |
| Prompt drift in long conversations | GPT may forget instructions | Use periodic memory refresh patterns |
| Flat file structure | Loses directory organization | Use naming prefixes |

## 8,000-character instruction limit

This is the most significant constraint. The full SKILL.md body often exceeds 8,000 characters.

### Condensation strategies

**Priority 1 — Extract to knowledge files:**
```
BEFORE (in instructions):
  Detailed 3-page API reference with examples

AFTER:
  Instructions: "For API details, see REF_api_reference.md"
  Knowledge file: REF_api_reference.md (full content)
```

**Priority 2 — Compress prose to bullets:**
```
BEFORE: "When processing PDF files, it is important to first
analyze the form structure to understand what fields are
available. This step ensures that subsequent operations
will target the correct form fields."

AFTER: "Step 1: Analyze form structure (identify available fields)"
```

**Priority 3 — Remove redundancy:**
- Drop "About this skill" sections (the GPT description handles this)
- Remove explanatory context the model already knows
- Eliminate duplicate information across sections

**Priority 4 — Use shorthand:**
```
BEFORE: "Use the following Python code to extract text:"
AFTER: "Extract text:"
```

### Character budget

| Section | Budget | Purpose |
|---------|--------|---------|
| Role/purpose | ~500 chars | What the GPT does |
| Core workflow | ~3,000 chars | Step-by-step procedures |
| Key rules | ~2,000 chars | Critical constraints and rules |
| File pointers | ~1,500 chars | References to knowledge files |
| Edge cases | ~1,000 chars | Warnings and special handling |

### Overflow strategy

When content exceeds 8,000 characters after condensation:

1. Create `REF_extended_instructions.md` with overflow content
2. Add to instructions: "For detailed procedures, read REF_extended_instructions.md"
3. Structure the overflow file with clear headers for RAG retrieval

## Code Interpreter

GPTs can execute Python code in a sandboxed environment via Code Interpreter.

### Capabilities

- Python execution in a Jupyter-like sandbox
- File upload and download
- Common packages pre-installed (pandas, numpy, matplotlib, etc.)
- No network access
- No persistent storage between sessions

### When to use Code Interpreter

| Scenario | Use Code Interpreter? |
|----------|----------------------|
| Data processing (CSV, JSON) | Yes |
| Chart/visualization generation | Yes |
| Text file manipulation | Yes |
| PDF processing (with pypdf) | Maybe — check if package available |
| API calls | No — use Actions instead |
| File system operations | No — sandboxed |
| Package installation | Limited — only pre-installed packages |

### Script conversion for Code Interpreter

For scripts compatible with Code Interpreter:

1. Upload the `.py` file as a knowledge file (keep original extension)
2. In instructions, tell the GPT: "Execute scripts/[name].py using Code Interpreter"
3. The GPT will read and execute the code in its sandbox

For scripts NOT compatible:
1. Convert to instructional markdown (same as Gem conversion)
2. Name as `SCRIPT_[name].md`

## Actions for API integration

GPT Actions allow calling external APIs. This partially replaces script-based API calls in Agent Skills.

### When to use Actions

- The skill calls well-defined REST APIs
- Authentication can be configured (API key, OAuth, none)
- The API is publicly accessible
- Response format is JSON

### Creating an Action

1. Write an OpenAPI 3.0 specification for each endpoint
2. Configure authentication in GPT Builder
3. Add to instructions: "Use the [action-name] action to [purpose]"

### Limitations

- Cannot call internal/private APIs
- OAuth flow can be complex to configure
- Rate limits apply
- Response must be processable by the GPT

## Knowledge file retrieval (RAG)

GPTs use retrieval-augmented generation to search knowledge files. Content is chunked and embedded for semantic search.

### Optimizing for RAG

1. **Use clear section headers** — Headers help chunk boundaries
2. **Front-load key information** — First sentences of sections are most likely to be retrieved
3. **Keep related content together** — Don't split a topic across multiple files
4. **Use descriptive file names** — File names influence retrieval relevance
5. **Avoid very large files** — Split files over 50 pages for better chunking

### RAG limitations

- May not retrieve all relevant chunks for a query
- Semantic search can miss exact technical terms
- No guarantee of complete file reading
- Long conversations may reduce retrieval quality

### Mitigation patterns

```
In instructions:
"IMPORTANT: When answering questions about [topic], always
retrieve and read REF_[topic].md before responding."
```

Explicit retrieval instructions help ensure critical files are read.

## Asset handling

| Asset Type | GPT Strategy |
|------------|-------------|
| Templates (PPTX, DOCX) | Upload directly (counts toward 20-file limit) |
| Images (PNG, JPG, SVG) | Upload directly |
| Fonts (TTF, OTF) | Cannot use — reference by name |
| Large files (up to 512 MB) | Upload directly |
| CSV/JSON data | Upload for Code Interpreter processing |

## Naming conventions

Use consistent prefixes for all knowledge files:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `REF_` | Reference documentation | `REF_api_reference.md` |
| `SCRIPT_` | Converted script logic (or .py for Code Interpreter) | `SCRIPT_validate.md` |
| `ASSET_` | Binary assets | `ASSET_template.pptx` |
| `WORKFLOW_` | Multi-step procedures | `WORKFLOW_deployment.md` |

### Flattening nested paths

Replace directory separators with underscores:
```
references/workflows/create.md  →  REF_workflows_create.md
scripts/utils/helpers.py        →  SCRIPT_utils_helpers.md (or .py)
assets/templates/report.docx    →  ASSET_templates_report.docx
```

## Quality degradation analysis

### What gets lost in conversion

| Skill Feature | Loss Level | Mitigation |
|---------------|------------|------------|
| Script execution | Medium | Code Interpreter handles pure Python; convert others |
| Progressive loading | Medium | Pre-consolidate into instructions + knowledge files |
| Directory hierarchy | Low | Naming convention preserves semantics |
| Unlimited references | Low | 20-file limit is usually sufficient |
| Unlimited instructions | High | 8K char limit requires aggressive condensation |
| Tool integrations | Medium | Actions can replicate REST API calls |

### Capability retention by skill type

| Skill Type | GPT Retention |
|------------|---------------|
| Documentation/Knowledge | ~95% |
| Workflow guidance | ~85% |
| Code generation guidance | ~80% |
| Automated tasks | ~50% (with Code Interpreter) |
| External API integration | ~70% (with Actions) |

### GPT-specific opportunities

- **Code Interpreter**: Can execute Python in sandbox — partial script execution recovery
- **Actions**: REST API integration for external services
- **Larger file limit**: 512 MB per file, 20 files total
- **DALL-E integration**: Built-in image generation
- **Browsing**: Can access web content (if enabled)
