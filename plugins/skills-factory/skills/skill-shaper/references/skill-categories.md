# Skill Categories

Three archetypes cover most skills. Identifying your skill's category early shapes design decisions around structure, degrees of freedom, and progressive disclosure.

## Contents

- [Document and asset creation](#document-and-asset-creation)
- [Workflow automation](#workflow-automation)
- [MCP enhancement](#mcp-enhancement)
- [Composability principles](#composability-principles)

## Document and asset creation

Skills that produce files: PDFs, images, ebooks, presentations, websites.

**Characteristics**:
- Template-heavy — assets and reference files define the output format
- Scripts handle rendering, conversion, or compilation
- Output quality depends on examples and templates more than instructions

**Typical structure**:
```
brand-report/
├── SKILL.md            # Workflow: gather content → apply template → render
├── scripts/            # render_pdf.py, validate_output.py
├── references/         # brand-guidelines.md, page-layouts.md
└── assets/             # logo.png, fonts/, templates/
```

**Design guidance**:
- **Degrees of freedom**: Low to medium. Templates constrain output format; content varies.
- **Progressive disclosure**: Keep the creation workflow in SKILL.md. Move template details and brand guidelines to references.
- **Common pitfall**: Embedding large templates directly in SKILL.md. Always use assets/ for templates and references/ for template documentation.

**Examples in this repository**: `pdf-factory`, `epub-creator`, `site-factory`, `brand-bluewaves`

## Workflow automation

Skills that guide Claude through multi-step processes with decision points and validation loops.

**Characteristics**:
- Sequential or conditional steps with clear entry/exit criteria
- Validation and feedback loops between steps
- May coordinate scripts, file operations, or external tools

**Typical structure**:
```
data-pipeline/
├── SKILL.md            # Workflow steps with decision points
├── scripts/            # validate.py, transform.py, verify.py
└── references/         # schema.md, error-codes.md
```

**Design guidance**:
- **Degrees of freedom**: Medium. The workflow structure is fixed; individual steps allow flexibility.
- **Progressive disclosure**: Keep the workflow overview and decision criteria in SKILL.md. Move step-specific details to references.
- **Common pitfall**: Overspecifying every step. Use high freedom for judgment-based steps and low freedom only for fragile operations.

**Examples in this repository**: `athena-package`, `skill-shaper`, `chart-designer`

## MCP enhancement

Skills that add domain intelligence and tool guidance for MCP (Model Context Protocol) servers.

**Characteristics**:
- Provide domain knowledge that helps Claude use MCP tools effectively
- Use fully qualified tool names (`ServerName:tool_name`)
- May coordinate across multiple MCP servers

**Typical structure**:
```
sales-analytics/
├── SKILL.md            # When to use which tools, domain terminology
└── references/         # schema.md, metrics.md, query-patterns.md
```

**Design guidance**:
- **Degrees of freedom**: High. The skill provides knowledge; Claude decides how to apply it.
- **Progressive disclosure**: Keep tool selection guidance and key domain concepts in SKILL.md. Move detailed schemas and query patterns to references.
- **Common pitfall**: Duplicating MCP tool documentation. Focus on *when* and *why* to use tools, not *how* — the MCP server already provides tool descriptions.

## Composability principles

Skills work best when they are narrowly scoped and designed for combination.

**One concern per skill**: A skill that processes PDFs should not also create charts. Split into separate skills that can be used together.

**Scoped descriptions**: Broad descriptions cause overtriggering and make skills compete with each other. Be specific:
- **Too broad**: "Helps with documents and data visualization"
- **Focused**: "Extract text and tables from PDF files, fill PDF forms, merge PDFs"

**Compatible interfaces**: When skills may work together, use consistent terminology and formats. If one skill outputs markdown and another consumes it, document this interface.

**Avoid monolithic skills**: If a SKILL.md exceeds 300 lines, consider whether it's actually two skills. Signs of a monolithic skill:
- Multiple unrelated trigger phrases
- Sections that are never used together
- Users only need half the skill's functionality at a time
