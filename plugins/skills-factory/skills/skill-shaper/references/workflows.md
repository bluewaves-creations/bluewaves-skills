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

## Subagent Delegation

Fork work to specialized subagents for parallel or isolated execution.

```markdown
## Parallel Processing
1. Divide input into N chunks
2. Spawn N subagents, each processing one chunk
3. Collect results and merge
```

Use `isolation: "worktree"` for subagents that modify files, preventing conflicts.

## Dynamic Context Injection

Use `` !`command` `` to inject runtime context:

```markdown
Current directory: !`pwd`
Git branch: !`git branch --show-current`
```

Runs at load time, before the model processes the skill.

## Visual Output Pattern

For skills producing results the user needs to inspect visually:

```markdown
## Reviewing Results
1. Generate self-contained HTML with embedded CSS and data
2. Write to /tmp/<skill-name>-result.html
3. Open in browser: `open /tmp/<skill-name>-result.html`
4. Wait for user feedback before proceeding
```
