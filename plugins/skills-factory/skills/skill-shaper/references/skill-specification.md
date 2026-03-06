# Skill Specification

Technical specification for SKILL.md format, frontmatter fields, naming rules, and validation.

## Directory Structure

```
skill-name/
├── SKILL.md           (required)
├── scripts/           (optional) Executable code
├── references/        (optional) Documentation for context
└── assets/            (optional) Files used in output
```

The directory name MUST match the `name` field in SKILL.md frontmatter.

## SKILL.md Format

### Frontmatter (YAML)

Required fields: `name`, `description`. Optional fields listed below.

```yaml
---
name: skill-name
description: >
  What this skill does and when to use it.
  Max 1024 characters.
allowed-tools: Bash, Read, Write
license: MIT
---
```

### Frontmatter Fields

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | Hyphen-case, max 64 chars, `[a-z0-9-]`, no leading/trailing/consecutive hyphens |
| `description` | Yes | Max 1024 chars, no angle brackets (`<` `>`) |
| `allowed-tools` | No | Comma-separated tool names |
| `license` | No | SPDX identifier (e.g., MIT, Apache-2.0) |
| `compatibility` | No | Max 500 chars. Environment requirements |
| `metadata` | No | Arbitrary key-value pairs |
| `context` | No | When to load: `project`, `personal`, `enterprise` |
| `agent` | No | Agent type for subagent-based skills |
| `hooks` | No | Hook definitions for the skill |
| `model` | No | Preferred model ID |
| `user-invocable` | No | `true` (default) or `false` — whether users can invoke via `/skill-name` |
| `disable-model-invocation` | No | `true` to prevent automatic triggering |
| `argument-hint` | No | Hint text shown in `/` menu for expected arguments |

### Name Rules

- Hyphen-case: lowercase letters, digits, hyphens only
- Max 64 characters
- Cannot start or end with a hyphen
- Cannot contain consecutive hyphens (`--`)
- Must match the directory name exactly

Valid: `pdf-processing`, `data-analysis`, `code-review`
Invalid: `PDF-Processing` (uppercase), `-pdf` (leading hyphen), `pdf--processing` (consecutive)

### Description Guidelines

- Max 1024 characters, no angle brackets
- Include both what the skill does AND when to use it
- All "when to use" information goes here — the body is only loaded after triggering
- Be assertive and territory-claiming (see authoring-best-practices.md)

## String Substitutions

Available in skill body and descriptions:

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | Full argument string from `/skill-name <args>` |
| `$1`, `$2`, ... `$N` | Positional arguments |
| `${CLAUDE_SESSION_ID}` | Unique session identifier |

## Dynamic Context Injection

The `` !`command` `` syntax runs a shell command during skill loading and injects its output:

```markdown
Current git branch: !`git branch --show-current`
```

Runs at load time, before the model sees the content.

## Skill Scope and Priority

When multiple skills match, priority: enterprise > personal > project > plugin.

## Progressive Disclosure

Three loading levels:
1. **Metadata** (name + description) — Always in context (~100 tokens)
2. **SKILL.md body** — When skill triggers (target: <500 lines, <5000 tokens)
3. **Bundled resources** — As needed (unlimited — scripts execute without loading)

## File References

- Use relative paths from SKILL.md
- Keep references one level deep (no nested references)
- For files >100 lines, include a table of contents
- For files >10k words, include grep search patterns in SKILL.md

## Validation

**Primary:** `skills-ref validate <skill-dir>` (official Anthropic validator)

**Fallback:** `quick_validate.py` checks: SKILL.md exists, valid YAML, required fields, name format, description length, no unexpected keys.

Install: `uv pip install -e deps/agentskills/skills-ref/`
