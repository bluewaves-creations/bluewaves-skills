# Agent Skills Specification

Reference for the complete Agent Skills format. Use this when verifying frontmatter constraints, naming rules, and directory structure requirements.

## Contents

- [Directory structure](#directory-structure)
- [SKILL.md format](#skillmd-format)
- [Frontmatter fields](#frontmatter-fields)
- [Body content](#body-content)
- [Optional directories](#optional-directories)
- [Progressive disclosure](#progressive-disclosure)
- [File references](#file-references)
- [Validation](#validation)

## Directory structure

A skill is a directory containing at minimum a `SKILL.md` file:

```
skill-name/
├── SKILL.md          # Required
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
└── assets/           # Optional: templates, resources
```

## SKILL.md format

The `SKILL.md` file must contain YAML frontmatter followed by Markdown content.

### Frontmatter (required)

```yaml
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

With optional fields:

```yaml
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents.
license: Apache-2.0
metadata:
  author: example-org
  version: "1.0"
---
```

## Frontmatter fields

| Field           | Required | Constraints                                                                                                       |
| --------------- | -------- | ----------------------------------------------------------------------------------------------------------------- |
| `name`          | Yes      | Max 64 characters. Lowercase letters, numbers, and hyphens only. Must not start or end with a hyphen.             |
| `description`   | Yes      | Max 1024 characters. Non-empty. Describes what the skill does and when to use it.                                 |
| `license`       | No       | License name or reference to a bundled license file.                                                              |
| `compatibility` | No       | Max 500 characters. Indicates environment requirements (intended product, system packages, network access, etc.). |
| `metadata`      | No       | Arbitrary key-value mapping for additional metadata.                                                              |
| `allowed-tools` | No       | Space-delimited list of pre-approved tools the skill may use. (Experimental)                                      |

### `name` field

- Must be 1-64 characters
- May only contain lowercase alphanumeric characters and hyphens (`a-z`, `0-9`, `-`)
- Must not start or end with `-`
- Must not contain consecutive hyphens (`--`)
- Must match the parent directory name

Valid examples: `pdf-processing`, `data-analysis`, `code-review`

Invalid examples:
- `PDF-Processing` — uppercase not allowed
- `-pdf` — cannot start with hyphen
- `pdf--processing` — consecutive hyphens not allowed

### `description` field

- Must be 1-1024 characters
- Should describe both what the skill does and when to use it
- Should include specific keywords that help agents identify relevant tasks
- Cannot contain angle brackets (`<` or `>`)

Good example:
```yaml
description: Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.
```

Poor example:
```yaml
description: Helps with PDFs.
```

### `license` field

- Specifies the license applied to the skill
- Keep it short (either the name of a license or the name of a bundled license file)

Example: `license: Proprietary. LICENSE.txt has complete terms`

### `compatibility` field

- Must be 1-500 characters if provided
- Only include if the skill has specific environment requirements

Examples:
- `compatibility: Designed for Claude Code (or similar products)`
- `compatibility: Requires git, docker, jq, and access to the internet`

### `metadata` field

- A map from string keys to string values
- Clients can use this to store additional properties not defined by the Agent Skills spec

Example:
```yaml
metadata:
  author: example-org
  version: "1.0"
```

### `allowed-tools` field

- A space-delimited list of tools that are pre-approved to run
- Experimental. Support may vary between agent implementations.

Example: `allowed-tools: Bash(git:*) Bash(jq:*) Read`

## Body content

The Markdown body after the frontmatter contains the skill instructions. There are no format restrictions. Write whatever helps agents perform the task effectively.

Recommended sections:
- Step-by-step instructions
- Examples of inputs and outputs
- Common edge cases

The agent loads the entire body once it decides to activate the skill. Consider splitting longer content into referenced files.

## Optional directories

### scripts/

Contains executable code that agents can run. Scripts should:
- Be self-contained or clearly document dependencies
- Include helpful error messages
- Handle edge cases gracefully

Supported languages depend on the agent implementation. Common options: Python, Bash, JavaScript.

### references/

Contains additional documentation that agents can read when needed:
- Detailed technical references
- Form templates or structured data formats
- Domain-specific files (finance.md, legal.md, etc.)

Keep individual reference files focused. Agents load these on demand, so smaller files mean less context usage.

### assets/

Contains static resources:
- Templates (document templates, configuration templates)
- Images (diagrams, examples)
- Data files (lookup tables, schemas)

## Progressive disclosure

Skills should be structured for efficient use of context:

1. **Metadata** (~100 tokens): The `name` and `description` fields are loaded at startup for all skills
2. **Instructions** (< 5000 tokens recommended): The full `SKILL.md` body is loaded when the skill is activated
3. **Resources** (as needed): Files in `scripts/`, `references/`, or `assets/` are loaded only when required

Keep your main `SKILL.md` under 500 lines. Move detailed reference material to separate files.

## File references

When referencing other files in your skill, use relative paths from the skill root:

```markdown
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script:
scripts/extract.py
```

Keep file references one level deep from `SKILL.md`. Avoid deeply nested reference chains.

## Validation

Use the `skills-ref` reference library to validate your skills:

```bash
skills-ref validate ./my-skill
```

This checks that your `SKILL.md` frontmatter is valid and follows all naming conventions.

Install from the agentskills repository:

```bash
uv pip install -e deps/agentskills/skills-ref/
```
