# Skill Authoring Best Practices

Practical guidance for writing effective skills that Claude can discover and use successfully.

## Contents

- [Core principles](#core-principles)
- [Naming conventions](#naming-conventions)
- [Writing effective descriptions](#writing-effective-descriptions)
- [Content guidelines](#content-guidelines)
- [Common patterns](#common-patterns)
- [Workflows and feedback loops](#workflows-and-feedback-loops)
- [Skills with executable code](#skills-with-executable-code)
- [Evaluation and iteration](#evaluation-and-iteration)
- [Anti-patterns to avoid](#anti-patterns-to-avoid)
- [Checklist for effective skills](#checklist-for-effective-skills)

## Core principles

### Concise is key

The context window is a public good. Your skill shares the context window with everything else Claude needs: system prompt, conversation history, other skills' metadata, and the actual user request.

Not every token has an immediate cost. At startup, only the metadata (name and description) is pre-loaded. Claude reads SKILL.md only when the skill becomes relevant. However, being concise in SKILL.md still matters: once Claude loads it, every token competes with conversation history and other context.

**Default assumption**: Claude is already very smart. Only add context Claude doesn't already have.

Challenge each piece of information:
- "Does Claude really need this explanation?"
- "Can I assume Claude knows this?"
- "Does this paragraph justify its token cost?"

**Good example** (~50 tokens):
````markdown
## Extract PDF text

Use pdfplumber for text extraction:

```python
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
````

**Bad example** (~150 tokens):
```markdown
## Extract PDF text

PDF (Portable Document Format) files are a common file format that contains
text, images, and other content. To extract text from a PDF, you'll need to
use a library. There are many libraries available for PDF processing, but we
recommend pdfplumber because it's easy to use...
```

The concise version assumes Claude knows what PDFs are and how libraries work.

### Set appropriate degrees of freedom

Match the level of specificity to the task's fragility and variability.

**High freedom** (text-based instructions): Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.

**Medium freedom** (pseudocode or scripts with parameters): Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.

**Low freedom** (specific scripts, few parameters): Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

**Analogy**: Think of Claude as a robot exploring a path:
- **Narrow bridge with cliffs**: One safe way forward. Provide exact instructions (low freedom).
- **Open field**: Many paths to success. Give general direction (high freedom).

### Test with all models you plan to use

Skills act as additions to models, so effectiveness depends on the underlying model. Test your skill with all the models you plan to use it with.

- **Claude Haiku** (fast, economical): Does the skill provide enough guidance?
- **Claude Sonnet** (balanced): Is the skill clear and efficient?
- **Claude Opus** (powerful reasoning): Does the skill avoid over-explaining?

What works perfectly for Opus might need more detail for Haiku.

## Naming conventions

Use consistent naming patterns to make skills easier to reference. Recommended: **gerund form** (verb + -ing) for skill names, as this clearly describes the activity the skill provides.

The `name` field must use lowercase letters, numbers, and hyphens only.

**Good naming examples (gerund form)**:
- `processing-pdfs`
- `analyzing-spreadsheets`
- `managing-databases`

**Acceptable alternatives**:
- Noun phrases: `pdf-processing`, `spreadsheet-analysis`
- Action-oriented: `process-pdfs`, `analyze-spreadsheets`

**Avoid**:
- Vague names: `helper`, `utils`, `tools`
- Overly generic: `documents`, `data`, `files`
- Reserved words: `anthropic-helper`, `claude-tools`
- Inconsistent patterns within your skill collection

## Writing effective descriptions

The `description` field enables skill discovery and should include both what the skill does and when to use it.

**Always write in third person.** The description is injected into the system prompt, and inconsistent point-of-view can cause discovery problems.

- **Good:** "Processes Excel files and generates reports"
- **Avoid:** "I can help you process Excel files"
- **Avoid:** "You can use this to process Excel files"

**Be specific and include key terms.** Claude uses the description to choose the right skill from potentially 100+ available skills.

Effective examples:

```yaml
# PDF Processing
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.

# Excel Analysis
description: Analyze Excel spreadsheets, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.

# Git Commit Helper
description: Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages or reviewing staged changes.
```

Avoid vague descriptions:
```yaml
description: Helps with documents
description: Processes data
description: Does stuff with files
```

## Content guidelines

### Avoid time-sensitive information

Don't include information that will become outdated. Use an "old patterns" section for deprecated approaches:

```markdown
## Current method

Use the v2 API endpoint: `api.example.com/v2/messages`

## Old patterns

<details>
<summary>Legacy v1 API (deprecated 2025-08)</summary>
The v1 API used: `api.example.com/v1/messages`
This endpoint is no longer supported.
</details>
```

### Use consistent terminology

Choose one term and use it throughout the skill:

- **Good**: Always "API endpoint", always "field", always "extract"
- **Bad**: Mix "API endpoint"/"URL"/"API route"; mix "field"/"box"/"element"

## Common patterns

### Template pattern

Provide templates for output format. Match strictness to your needs.

**For strict requirements** (API responses, data formats):
```markdown
## Report structure

ALWAYS use this exact template structure:
[template here]
```

**For flexible guidance** (when adaptation is useful):
```markdown
## Report structure

Here is a sensible default format, but use your best judgment:
[template here]
```

### Examples pattern

For skills where output quality depends on seeing examples, provide input/output pairs:

````markdown
## Commit message format

Generate commit messages following these examples:

**Example 1:**
Input: Added user authentication with JWT tokens
Output:
```
feat(auth): implement JWT-based authentication
Add login endpoint and token validation middleware
```
````

Examples help Claude understand the desired style and detail level more clearly than descriptions alone.

### Conditional workflow pattern

Guide Claude through decision points:

```markdown
## Document modification workflow

1. Determine the modification type:
   **Creating new content?** → Follow "Creation workflow" below
   **Editing existing content?** → Follow "Editing workflow" below

2. Creation workflow: [steps]
3. Editing workflow: [steps]
```

## Workflows and feedback loops

### Use workflows for complex tasks

Break complex operations into clear, sequential steps. For complex workflows, provide a checklist that Claude can copy and check off as it progresses.

```markdown
## PDF form filling workflow

Task Progress:
- [ ] Step 1: Analyze the form (run analyze_form.py)
- [ ] Step 2: Create field mapping (edit fields.json)
- [ ] Step 3: Validate mapping (run validate_fields.py)
- [ ] Step 4: Fill the form (run fill_form.py)
- [ ] Step 5: Verify output (run verify_output.py)
```

### Implement feedback loops

**Common pattern**: Run validator -> fix errors -> repeat

This pattern greatly improves output quality.

```markdown
## Document editing process

1. Make your edits to `word/document.xml`
2. **Validate immediately**: `python scripts/validate.py unpacked_dir/`
3. If validation fails:
   - Review the error message carefully
   - Fix the issues
   - Run validation again
4. **Only proceed when validation passes**
5. Rebuild: `python scripts/pack.py unpacked_dir/ output.docx`
```

## Skills with executable code

### Solve, don't punt

When writing scripts, handle error conditions rather than punting to Claude.

**Good**: Handle errors explicitly with fallback behavior and clear messages.
**Bad**: Just `open(path).read()` and let Claude figure out failures.

Configuration parameters should be justified and documented to avoid "voodoo constants."

### Provide utility scripts

Pre-made scripts offer advantages over Claude-generated code:
- More reliable than generated code
- Save tokens (no need to include code in context)
- Save time (no code generation required)
- Ensure consistency across uses

Make clear whether Claude should **execute** the script or **read** it as reference.

### Create verifiable intermediate outputs

For complex, open-ended tasks, use the "plan-validate-execute" pattern: analyze -> **create plan file** -> **validate plan** -> execute -> verify.

Make validation scripts verbose with specific error messages to help Claude fix issues.

### Package dependencies

List required packages in your SKILL.md and verify availability. Skills run in code execution environments with platform-specific limitations.

### MCP tool references

If your skill uses MCP tools, always use fully qualified tool names: `ServerName:tool_name`

Example: `BigQuery:bigquery_schema`, `GitHub:create_issue`

## Evaluation and iteration

### Build evaluations first

Create evaluations BEFORE writing extensive documentation. This ensures your skill solves real problems.

**Evaluation-driven development:**
1. **Identify gaps**: Run Claude on representative tasks without a skill. Document specific failures.
2. **Create evaluations**: Build three scenarios that test these gaps.
3. **Establish baseline**: Measure Claude's performance without the skill.
4. **Write minimal instructions**: Create just enough content to address gaps and pass evaluations.
5. **Iterate**: Execute evaluations, compare against baseline, and refine.

### Develop skills iteratively with Claude

Work with one instance of Claude ("Claude A") to create a skill that will be used by other instances ("Claude B"):

1. Complete a task without a skill using normal prompting
2. Identify the reusable pattern from what context you provided
3. Ask Claude A to create a skill capturing that pattern
4. Review for conciseness
5. Improve information architecture
6. Test on similar tasks with Claude B (fresh instance with skill loaded)
7. Iterate based on Claude B's behavior

### Observe how Claude navigates skills

Watch for:
- **Unexpected exploration paths**: Structure may not be as intuitive as you thought
- **Missed connections**: Links might need to be more explicit
- **Overreliance on certain sections**: Consider promoting that content to SKILL.md
- **Ignored content**: Might be unnecessary or poorly signaled

## Anti-patterns to avoid

- **Windows-style paths**: Always use forward slashes (`scripts/helper.py`), not backslashes
- **Too many options**: Provide a default with an escape hatch, not a buffet of choices
- **Assuming tools are installed**: Be explicit about dependencies

## Checklist for effective skills

### Core quality
- [ ] Description is specific and includes key terms
- [ ] Description includes both what the skill does and when to use it
- [ ] SKILL.md body is under 500 lines
- [ ] Additional details are in separate files (if needed)
- [ ] No time-sensitive information
- [ ] Consistent terminology throughout
- [ ] Examples are concrete, not abstract
- [ ] File references are one level deep
- [ ] Progressive disclosure used appropriately
- [ ] Workflows have clear steps

### Code and scripts
- [ ] Scripts solve problems rather than punt to Claude
- [ ] Error handling is explicit and helpful
- [ ] No "voodoo constants" (all values justified)
- [ ] Required packages listed and verified as available
- [ ] No Windows-style paths
- [ ] Validation/verification steps for critical operations
- [ ] Feedback loops included for quality-critical tasks

### Testing
- [ ] At least three evaluations created
- [ ] Tested with Haiku, Sonnet, and Opus
- [ ] Tested with real usage scenarios
- [ ] Team feedback incorporated (if applicable)
