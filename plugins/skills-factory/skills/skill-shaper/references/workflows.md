# Workflow Patterns

Common patterns for structuring multi-step skill workflows.

## Contents

- [Sequential workflows](#sequential-workflows)
- [Conditional workflows](#conditional-workflows)
- [Iterative refinement](#iterative-refinement)
- [Plan-validate-execute](#plan-validate-execute)
- [Multi-MCP orchestration](#multi-mcp-orchestration)

## Sequential Workflows

For complex tasks, break operations into clear, sequential steps. It is often helpful to give Claude an overview of the process towards the beginning of SKILL.md:

```markdown
Filling a PDF form involves these steps:

1. Analyze the form (run analyze_form.py)
2. Create field mapping (edit fields.json)
3. Validate mapping (run validate_fields.py)
4. Fill the form (run fill_form.py)
5. Verify output (run verify_output.py)
```

## Conditional Workflows

For tasks with branching logic, guide Claude through decision points:

```markdown
1. Determine the modification type:
   **Creating new content?** → Follow "Creation workflow" below
   **Editing existing content?** → Follow "Editing workflow" below

2. Creation workflow: [steps]
3. Editing workflow: [steps]
```

## Iterative Refinement

For tasks where the first output is rarely perfect, build a generate-validate-fix loop:

```markdown
## Document generation workflow

1. Generate the initial output (run generate.py)
2. Validate the output (run validate.py)
3. If validation fails:
   - Review the error messages
   - Fix the identified issues
   - Return to step 1
4. Only proceed when validation passes
5. Finalize the output (run finalize.py)
```

**When to use**: Output quality is critical and automated validation is possible (document formatting, code generation, data transformation).

**Key design points**:
- Set a maximum iteration count (3-5) to prevent infinite loops
- Make validation output specific and actionable so Claude can fix issues
- Each iteration should make the output strictly better — if not, the validation feedback needs improvement

## Plan-Validate-Execute

For complex, open-ended tasks, separate planning from execution to catch errors early:

```markdown
## Analysis workflow

1. **Analyze**: Read input files and understand requirements
2. **Plan**: Write a plan file (plan.md) describing each step
3. **Validate**: Review the plan for completeness and correctness
   - Are all required inputs available?
   - Are the steps in the right order?
   - Are edge cases addressed?
4. **Execute**: Follow the validated plan step by step
5. **Verify**: Compare final output against the plan's goals
```

**When to use**: Tasks with multiple valid approaches where an incorrect choice is expensive to redo (data migrations, multi-file refactors, complex document assembly).

**Key design points**:
- The plan file serves as a verifiable intermediate artifact
- Validation can be manual (Claude reviews its own plan) or automated (a script checks the plan)
- Separating planning from execution makes the skill more debuggable

## Multi-MCP Orchestration

For skills that coordinate data flow across multiple MCP tool servers:

```markdown
## Cross-platform report workflow

1. Fetch raw data from the database
   Tool: `Database:execute_query`
2. Transform and analyze the data
   (Claude processes the results directly)
3. Create visualizations
   Tool: `Charts:create_chart`
4. Assemble the final report
   Tool: `Documents:create_pdf`
```

**When to use**: The skill's value comes from coordinating tools that don't natively communicate with each other.

**Key design points**:
- Always use fully qualified tool names (`ServerName:tool_name`)
- Document the data format expected between steps (e.g., "Step 1 returns CSV; Step 3 expects a list of dictionaries")
- Handle partial failures — if one MCP server is unavailable, document the fallback behavior
- Keep orchestration logic in SKILL.md; keep server-specific details in reference files
