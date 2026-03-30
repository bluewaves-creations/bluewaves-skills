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
| `allowed-tools` | No | Comma-separated tool names. Supports patterns: `Bash(gh *)` allows only `gh` commands in Bash. |
| `license` | No | SPDX identifier (e.g., MIT, Apache-2.0) |
| `compatibility` | No | Max 500 chars. Environment requirements |
| `metadata` | No | Arbitrary key-value pairs |
| `context` | No | Set to `fork` to run in a forked subagent context |
| `agent` | No | Which subagent type to use when `context: fork` is set |
| `hooks` | No | Hook definitions scoped to this skill's lifecycle |
| `model` | No | Model to use when this skill is active |
| `user-invocable` | No | `true` (default) or `false` — whether users can invoke via `/skill-name` |
| `disable-model-invocation` | No | `true` to prevent Claude from automatically loading this skill |
| `argument-hint` | No | Hint text shown during autocomplete (e.g., `[issue-number]`) |

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
| `$ARGUMENTS` | Full argument string from `/skill-name <args>`. If not present in content, arguments are appended as `ARGUMENTS: <value>`. |
| `$ARGUMENTS[N]` | Access a specific argument by 0-based index (e.g., `$ARGUMENTS[0]` for the first argument) |
| `$0`, `$1`, ... `$N` | Shorthand for `$ARGUMENTS[0]`, `$ARGUMENTS[1]`, etc. |
| `${CLAUDE_SESSION_ID}` | Unique session identifier |

**Example using positional arguments:**

```yaml
---
name: migrate-component
description: Migrate a component from one framework to another
---

Migrate the $0 component from $1 to $2.
Preserve all existing behavior and tests.
```

Running `/migrate-component SearchBar React Vue` replaces `$0` with `SearchBar`, `$1` with `React`, `$2` with `Vue`.

## Dynamic Context Injection

The `` !`command` `` syntax runs a shell command during skill loading and injects its output:

```markdown
Current git branch: !`git branch --show-current`
```

Runs at load time, before the model sees the content. This is preprocessing — Claude only sees the final result.

## Invocation Control

Two fields control who can invoke a skill and how it appears in context:

| Frontmatter | User can invoke | Claude can invoke | When loaded into context |
|-------------|----------------|-------------------|------------------------|
| (default) | Yes | Yes | Description always in context, full skill loads when invoked |
| `disable-model-invocation: true` | Yes | No | Description not in context, full skill loads when user invokes |
| `user-invocable: false` | No | Yes | Description always in context, full skill loads when invoked |

**`disable-model-invocation: true`** — Use for workflows with side effects or where you want to control timing (`/deploy`, `/send-slack-message`). You don't want Claude deciding to deploy because your code looks ready.

**`user-invocable: false`** — Use for background knowledge that isn't actionable as a command. A `legacy-system-context` skill explains how an old system works — Claude should know this when relevant, but `/legacy-system-context` isn't a meaningful user action.

Note: `user-invocable` only controls menu visibility, not Skill tool access. Use `disable-model-invocation: true` to block programmatic invocation.

## context: fork and agent Interaction

When `context: fork` is set, the skill runs in an isolated subagent:

- SKILL.md content becomes the subagent's task prompt
- The `agent` field selects the execution environment: built-in (`Explore`, `Plan`, `general-purpose`) or custom (from `.claude/agents/`)
- If `agent` is omitted, defaults to `general-purpose`
- The subagent does NOT have access to conversation history
- CLAUDE.md files are still loaded

| Approach | System prompt | Task | Also loads |
|----------|--------------|------|------------|
| Skill with `context: fork` | From agent type | SKILL.md content | CLAUDE.md |
| Subagent with `skills` field | Subagent's markdown body | Claude's delegation message | Preloaded skills + CLAUDE.md |

**Warning:** `context: fork` only makes sense for skills with explicit task instructions. A skill containing only guidelines ("use these API conventions") gives the subagent no actionable prompt and returns without meaningful output.

**Example:**

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

Research $ARGUMENTS thoroughly:
1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

## Skill Scope and Priority

When multiple skills match, priority: enterprise > personal > project > plugin.

Plugin skills use a `plugin-name:skill-name` namespace, so they cannot conflict with other levels. If a skill and a legacy command (`.claude/commands/`) share the same name, the skill takes precedence.

### Automatic Discovery

Claude Code discovers skills from nested `.claude/skills/` directories when working with files in subdirectories. For example, editing files in `packages/frontend/` also discovers skills in `packages/frontend/.claude/skills/`. This supports monorepo setups where packages have their own skills.

Skills in directories added via `--add-dir` are loaded automatically and support live change detection — you can edit them during a session without restarting.

## Progressive Disclosure

Three loading levels:
1. **Metadata** (name + description) — Always in context (~100 tokens)
2. **SKILL.md body** — When skill triggers (target: <500 lines, <5000 tokens)
3. **Bundled resources** — As needed (unlimited — scripts execute without loading)

Skill descriptions share a character budget: ~2% of the context window (fallback: 16,000 characters). If you have many skills, some may be excluded. Run `/context` to check for warnings about excluded skills. Override with the `SLASH_COMMAND_TOOL_CHAR_BUDGET` environment variable.

## File References

- Use relative paths from SKILL.md
- Keep references one level deep (no nested references)
- For files >100 lines, include a table of contents
- For files >10k words, include grep search patterns in SKILL.md

## Validation

**Primary:** `skills-ref validate <skill-dir>` (official Anthropic validator)

**Fallback:** `quick_validate.py` checks: SKILL.md exists, valid YAML, required fields, name format, description length, no unexpected keys.

Install: `uv pip install -e deps/agentskills/skills-ref/`
