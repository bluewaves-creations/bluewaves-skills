# Distribution Guide

How to package, distribute, and position skills for different audiences and platforms.

## Contents

- [Distribution channels](#distribution-channels)
- [Packaging formats](#packaging-formats)
- [Positioning your skill](#positioning-your-skill)

## Distribution channels

### Individual upload (Claude.ai)

The simplest distribution method. Users upload skills via Claude.ai Settings > Capabilities.

**Best for**: Personal skills, prototyping, sharing with individuals.

**Process**:
1. Package the skill as a ZIP file
2. User opens Claude.ai > Settings > Capabilities
3. Upload the ZIP file
4. Skill is available immediately in new conversations

**Limitations**: Manual process, no version management, one user at a time.

### Claude Code plugin marketplace

Distribute skills as part of a Claude Code plugin for team or community use.

**Best for**: Team-wide skills, curated skill collections, skills bundled with commands and hooks.

**Process**:
1. Structure the skill within a plugin directory
2. Register the plugin in a marketplace (`marketplace.json`)
3. Users install via `/plugin install your-plugin@marketplace`

**Advantages**: Version management, bundled dependencies, discoverable through marketplace browsing.

### API and SDK usage

Attach skills programmatically via the Anthropic Messages API.

**Best for**: Automated pipelines, applications that use Claude as a backend, CI/CD integration.

**Usage**: Pass skill paths or content via the `container.skills` parameter in API calls. This enables applications to dynamically select which skills Claude uses based on the task context.

### GitHub hosting

Host skills in a public or private GitHub repository for sharing and collaboration.

**Best for**: Open-source skills, community contributions, version-controlled distribution.

**Process**:
1. Structure the repository with one or more skill directories
2. Users clone or download the repository
3. Skills can be uploaded to Claude.ai or installed via Claude Code

## Packaging formats

### `.skill` ZIP file

The standard portable format. Created by `package_skill.py`.

**Structure**:
```
skill-name.skill (ZIP)
└── skill-name/
    ├── SKILL.md
    ├── scripts/
    ├── references/
    └── assets/
```

**Usage**: Works with Claude.ai upload and Claude Code. Most portable format.

### Plain ZIP for Claude.ai

A standard ZIP file containing the skill directory. Functionally identical to `.skill` but with `.zip` extension.

**When to use**: When distributing to users who may not recognize the `.skill` extension.

### Directory for Claude Code

An unpackaged skill directory on the local filesystem.

**When to use**: During development, for skills managed within a plugin, or when version control (git) handles distribution.

### Choosing a format

| Scenario | Recommended format |
|----------|-------------------|
| Sharing with a colleague | `.skill` or plain ZIP |
| Publishing to a marketplace | Directory within a plugin |
| API integration | Directory (referenced by path) |
| Open-source distribution | GitHub repository with directories |
| Active development | Local directory |

## Positioning your skill

How you describe and present a skill affects adoption. Focus on outcomes, not implementation details.

### Lead with the problem solved

**Weak**: "Uses pdfplumber to extract text from PDF documents with configurable options"

**Strong**: "Turn any PDF into clean, structured text in seconds — handles scanned documents, tables, and forms"

### Use before/after examples

Show what changes for the user:

```
Without this skill:
  User: "Extract the data from quarterly-report.pdf"
  Claude: Writes extraction code from scratch, may miss tables, no error handling

With this skill:
  User: "Extract the data from quarterly-report.pdf"
  Claude: Uses optimized extraction pipeline, handles tables and forms,
          validates output quality, produces structured markdown
```

### Describe the scope clearly

Users need to know what a skill handles and what it doesn't. A clear scope prevents frustration:

```
This skill handles:
- Text extraction from standard and scanned PDFs
- Table extraction with structure preservation
- Form field reading and filling

This skill does NOT handle:
- PDF creation from scratch (see pdf-factory)
- Image extraction
- PDF encryption/decryption
```

### Target your audience

Match the description complexity to the intended user:

- **For developers**: Include API details, configuration options, script interfaces
- **For end users**: Focus on what they can ask Claude to do, with example queries
- **For teams**: Emphasize consistency, shared workflows, and integration with existing tools
