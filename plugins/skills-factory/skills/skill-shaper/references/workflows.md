# Workflow Patterns

Design patterns for multi-step processes in skills.

## Sequential Workflow

Steps in fixed order. Best when each step depends on the previous.

```markdown
## Workflow
### Step 1: Extract
Read the input file and extract structured data.
### Step 2: Transform
Apply business rules to transform the data.
### Step 3: Validate
Run validation — catches errors early, fixing them after output costs 10x more.
### Step 4: Generate
Produce the final output from validated data.
```

## Conditional Workflow

Different paths based on input. Use a decision tree at the top.

```markdown
## Decision Tree
- **New document** (no existing file) → Step 1: Create from template
- **Existing document** (file provided) → Step 2: Read and analyze
- **Batch processing** (multiple files) → Step 3: Process each
```

## Iterative Refinement

Repeated improvement with quality gates. Set max iterations (3-5).

```markdown
## Refinement Loop
1. Generate initial output
2. Validate against requirements
3. If passes → deliver
4. If fails → identify issues, adjust, repeat (max 3 iterations)
5. If still failing → present best attempt with issues noted
```

## Plan-Validate-Execute

Three-phase approach for complex tasks.

```markdown
## Approach
### Phase 1: Plan
Analyze input, produce concrete plan with steps, issues, estimates.
### Phase 2: Validate
Review plan: all inputs accounted for? Edge cases covered? Dependencies resolved?
### Phase 3: Execute
Follow validated plan step by step. Save intermediate results for debugging.
```

**Design points:** The plan is a verifiable artifact. Validation can be manual or automated. Separating planning from execution makes debugging easier.

## Multi-MCP Orchestration

Skills coordinating across multiple MCP tool servers.

```markdown
## Tools
- `database:query` — Run SQL queries
- `search:web_search` — Search the web
- `github:create_issue` — Create GitHub issues

## Workflow
1. Query database: `database:query`
2. Search for context: `search:web_search`
3. Generate report combining sources
4. Create tracking issue: `github:create_issue`
```

Always use fully qualified tool names (`ServerName:tool_name`). Document data format between steps.

## Subagent Delegation (context: fork)

Skills can fork work to specialized subagents using `context: fork` in frontmatter.

### Basic pattern

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:
1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

The `agent` field selects the execution environment:

| Agent type | Tools | Model | Best for |
|------------|-------|-------|----------|
| `Explore` | Read-only (Read, Glob, Grep) | Haiku | Fast codebase search |
| `Plan` | Read-only | Inherits | Research and planning |
| `general-purpose` | All tools | Inherits | Complex multi-step tasks |
| Custom (from `.claude/agents/`) | As configured | As configured | Specialized workflows |

If `agent` is omitted, defaults to `general-purpose`.

### Parallel processing pattern

```markdown
## Workflow
1. Divide input into N chunks
2. Spawn N subagents, each processing one chunk
3. Collect results and merge
```

### Isolated file modification

Use `isolation: "worktree"` for subagents that modify files, preventing conflicts with the main workspace.

### Key constraints
- Subagents do NOT have access to conversation history
- SKILL.md content becomes the subagent's task prompt — must be self-contained
- CLAUDE.md files are still loaded
- `context: fork` requires explicit task instructions — guidelines-only skills ("use these API conventions") give the subagent no actionable prompt

## Dynamic Context Injection

Use `` !`command` `` to inject runtime context:

```markdown
Current directory: !`pwd`
Git branch: !`git branch --show-current`
```

Runs at load time, before the model processes the skill.

## Capture Existing Conversation

When the user says "turn this into a skill," extract the workflow from conversation history rather than starting from scratch.

1. **Scan history** for tools used, sequence of steps, corrections the user made, input/output formats observed
2. **Identify the repeatable pattern** — what would a generic version of this workflow look like?
3. **Extract answers** to the Capture Intent questions from what already happened
4. **Fill gaps** by asking the user only what's missing — don't re-ask questions the conversation already answered
5. **Confirm** the extracted workflow before writing SKILL.md

This pattern avoids redundant questions and builds on work the user and Claude already did together.

## Visual Output Pattern

For skills producing results the user needs to inspect visually:

```markdown
## Reviewing Results
1. Generate self-contained HTML with embedded CSS and data
2. Write to /tmp/<skill-name>-result.html
3. Open in browser: `open /tmp/<skill-name>-result.html`
4. Wait for user feedback before proceeding
```

For headless environments (Cowork), use `--static <path>` to write HTML without starting a server.
