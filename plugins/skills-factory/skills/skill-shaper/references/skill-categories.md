# Skill Categories

Identifying your skill's category shapes design decisions around structure, testing, and templates. Use the `--category` flag in `init_skill.py` to get category-tailored scaffolding.

## Document and Asset Creation

Skills that produce files: PDFs, images, ebooks, presentations, websites.

**Characteristics:**
- Template-heavy — assets and references define output format
- Scripts handle rendering, conversion, or compilation
- Output quality depends on examples and templates

**Typical structure:**
```
brand-report/
├── SKILL.md            # Workflow: gather → template → render → validate
├── scripts/            # render_pdf.py, validate_output.py
├── references/         # brand-guidelines.md, page-layouts.md
└── assets/             # logo.png, fonts/, templates/
```

**Design:** Low-medium freedom. Templates constrain format; content varies. Keep creation workflow in SKILL.md, move template details to references.

**Init:** `init_skill.py <name> --path <dir> --category document-creation`

**Examples:** `pdf-factory`, `epub-creator`, `site-factory`, `brand-bluewaves`

## Workflow Automation

Skills that guide multi-step processes with decision points and validation.

**Characteristics:**
- Sequential or conditional steps with entry/exit criteria
- Validation and feedback loops
- May coordinate scripts, files, or tools

**Typical structure:**
```
data-pipeline/
├── SKILL.md            # Workflow steps with decision points
├── scripts/            # validate.py, transform.py, verify.py
└── references/         # schema.md, error-codes.md
```

**Design:** Medium freedom. Workflow is fixed; individual steps flex. High freedom for judgment; low freedom for fragile operations.

**Init:** `init_skill.py <name> --path <dir> --category workflow`

**Examples:** `athena-package`, `skill-shaper`, `chart-designer`

## MCP Enhancement

Skills that add domain intelligence for MCP tool servers.

**Characteristics:**
- Domain knowledge improves tool usage
- Fully qualified tool names (`ServerName:tool_name`)
- May coordinate across multiple servers

**Typical structure:**
```
sales-analytics/
├── SKILL.md            # Tool selection, domain concepts
└── references/         # schema.md, metrics.md, query-patterns.md
```

**Design:** High freedom. Skill provides knowledge; Claude decides application. Focus on when/why to use tools, not how (MCP provides that).

**Init:** `init_skill.py <name> --path <dir> --category mcp-enhancement`

## Subagent-Based Skills

Skills that fork work to specialized subagents.

**Characteristics:**
- Parallel or isolated execution
- Context: fork with agent type selection
- May use `isolation: "worktree"` for file-modifying agents

**Use when:** Tasks benefit from parallel processing, isolated environments, or specialized agent configurations.

## Knowledge / Reference Skills

Skills that provide domain knowledge without active workflows.

**Characteristics:**
- Often `user-invocable: false` — triggered by model, not user
- Reference-heavy, minimal scripts
- Enhance other skills' effectiveness

**Example:** A finance-terms skill that provides terminology when Claude encounters financial documents, regardless of which other skill is active.

## Category-to-Template Mapping

| Category | Init Flag | Starter Checks | Key Patterns |
|----------|-----------|----------------|--------------|
| Document creation | `--category document-creation` | file_exists, file_size_range | Template, visual output |
| Workflow | `--category workflow` | exit_code, contains | Sequential, plan-validate-execute |
| MCP enhancement | `--category mcp-enhancement` | contains (tool calls) | Multi-MCP orchestration |
| Generic | (default) | — | Flexible |

## Composability Principles

- **One concern per skill.** PDF processing + chart creation = two skills.
- **Scoped descriptions.** Specific beats broad. "Extract text from PDFs" not "Helps with documents."
- **Compatible interfaces.** When skills work together, use consistent terms and formats.
- **Watch for monoliths.** If SKILL.md > 300 lines with unrelated sections, consider splitting.
