# Testing and Debugging Skills

Comprehensive guide for testing skills at every level and debugging common problems.

## Contents

- [Testing levels](#testing-levels)
- [Testing areas](#testing-areas)
- [Debugging common problems](#debugging-common-problems)
- [Iteration signals](#iteration-signals)

## Testing levels

Test skills at increasing levels of automation. Start with manual testing and move to programmatic testing as the skill matures.

### Level 1: Manual testing (Claude.ai)

Upload the skill via Claude.ai Settings > Capabilities and test interactively.

**When to use**: During initial development and rapid iteration.

**Process**:
1. Package the skill (ZIP or `.skill` file)
2. Upload to Claude.ai
3. Send test queries in a fresh conversation
4. Observe triggering behavior, instruction following, and output quality
5. Iterate on SKILL.md and re-upload

**Tip**: Always start a new conversation after re-uploading. Cached skill metadata from prior conversations may mask changes.

### Level 2: Scripted testing (Claude Code)

Install the skill locally and test with Claude Code for faster iteration.

**When to use**: During active development when you need rapid feedback loops.

**Process**:
1. Point Claude Code at the skill directory
2. Run test queries directly in the terminal
3. Observe Claude's tool usage, file reads, and script execution
4. Check that Claude follows the intended workflow

**Advantages**: Faster iteration, visibility into Claude's reasoning, no re-upload needed.

### Level 3: Programmatic testing (Messages API)

Automate testing with the Anthropic Messages API using `container.skills`.

**When to use**: For regression testing, CI/CD integration, or testing at scale.

**Minimal example** (Python):

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    container={"skills": ["path/to/your-skill"]},
    messages=[{"role": "user", "content": "Your test query here"}],
)

# Assert on response content
assert "expected output" in response.content[0].text
```

**Advantages**: Repeatable, scriptable, can run across multiple models and queries.

## Testing areas

Every skill should be tested across three areas: triggering, functionality, and performance.

### Area 1: Trigger testing

Verify the skill activates for the right queries and stays silent for irrelevant ones.

**Positive triggers** — Write 5+ paraphrased queries that should activate the skill:

```
# For a PDF processing skill:
- "Extract text from this PDF"
- "Can you read this PDF document?"
- "Pull the tables out of report.pdf"
- "I need the content from this PDF file"
- "Parse the data in the attached PDF"
```

**Negative triggers** — Write 3+ queries that should NOT activate the skill:

```
# Should NOT trigger the PDF skill:
- "Write me a Python script"
- "Summarize this text file"
- "Help me with my Excel spreadsheet"
```

**What to look for**:
- Does the skill trigger on all positive queries?
- Does it stay silent on negative queries?
- Does it trigger on edge cases (abbreviations, synonyms, indirect references)?

### Area 2: Functional testing

Verify the skill produces correct output and handles edge cases.

**Happy path**: Test the primary use case end-to-end with realistic inputs.

**Edge cases**: Test boundary conditions:
- Empty or minimal input
- Very large input
- Missing optional parameters
- Unusual but valid input formats

**Error conditions**: Test graceful failure:
- Missing dependencies or tools
- Invalid file formats
- Network failures (if applicable)
- Permission errors

**Script testing**: If the skill includes scripts, run each script independently:
```bash
# Test with valid input
python scripts/process.py test_input.pdf

# Test with edge cases
python scripts/process.py empty.pdf
python scripts/process.py large_file.pdf
```

### Area 3: Performance comparison

Measure whether the skill actually improves Claude's performance on target tasks.

**Baseline**: Run 3+ representative tasks WITHOUT the skill loaded. Document the output quality, errors, and time to completion.

**With skill**: Run the same tasks WITH the skill loaded. Compare against baseline.

**Metrics to track**:
- Output correctness (does it produce the right result?)
- Instruction adherence (does it follow the workflow?)
- Efficiency (fewer retries, less trial-and-error?)
- Consistency (same quality across multiple runs?)

If the skill doesn't measurably improve at least one metric, reconsider whether the skill adds value or needs restructuring.

## Debugging common problems

### Skill doesn't trigger (undertriggering)

**Symptoms**: Claude doesn't use the skill even when it should.

**Causes and fixes**:

| Cause | Fix |
|-------|-----|
| Description too narrow | Add synonyms, related terms, and alternative phrasings |
| Missing key terms | Include the specific words users would say |
| Description too technical | Add plain-language triggers alongside technical terms |
| Competing with another skill | Make the description more specific to distinguish from similar skills |

**Example fix** — Before:
```yaml
description: Processes PDF documents using pdfplumber extraction.
```

After:
```yaml
description: Extract text and tables from PDF files, fill PDF forms, and merge multiple PDFs. Use when working with PDF documents, reading PDFs, or when the user mentions PDFs, forms, or document extraction.
```

### Skill triggers too often (overtriggering)

**Symptoms**: Claude activates the skill for unrelated queries.

**Causes and fixes**:

| Cause | Fix |
|-------|-----|
| Description too broad | Narrow scope with specific qualifiers |
| Generic keywords | Replace "documents" with "PDF documents", "data" with "Excel spreadsheets" |
| Missing negative context | Add "Do NOT use for..." in the description if needed |

### Instructions not followed

**Symptoms**: Skill triggers but Claude ignores key instructions.

**Causes and fixes**:

| Cause | Fix |
|-------|-----|
| SKILL.md too verbose | Cut ruthlessly — Claude skims long documents |
| Critical info buried | Move important instructions to the top of relevant sections |
| Ambiguous wording | Use imperative form with explicit steps |
| Conflicting instructions | Remove contradictions; ensure one clear path |
| Too many options | Provide a default with an escape hatch, not a buffet |

### Execution fails

**Symptoms**: Scripts error out or produce wrong output.

**Causes and fixes**:

| Cause | Fix |
|-------|-----|
| Missing dependencies | List all requirements; verify with a clean environment |
| Hardcoded paths | Use relative paths from the skill root |
| Platform differences | Test on target platforms; avoid platform-specific commands |
| Script bugs | Test scripts independently before including in the skill |
| Permission errors | Document required permissions; use appropriate file modes |

### Context overflow

**Symptoms**: Claude's output quality degrades or it loses track of instructions.

**Causes and fixes**:

| Cause | Fix |
|-------|-----|
| SKILL.md too long | Split into SKILL.md + reference files; stay under 500 lines |
| Loading unnecessary references | Add clear conditions for when to read each reference |
| Large scripts loaded into context | Design scripts to be executed, not read into context |

### Skill won't upload or validate

**Symptoms**: Upload fails or validation reports errors.

**Common issues**:

| Issue | Fix |
|-------|-----|
| Invalid YAML frontmatter | Check for missing `---` delimiters, proper indentation |
| Angle brackets in description | Replace `<` and `>` with plain text |
| Name doesn't match directory | Ensure `name` field matches the parent folder name exactly |
| Name has invalid characters | Use only lowercase letters, digits, and hyphens |
| File too large | Split content into reference files |

## Iteration signals

Use this table to map observed problems to specific actions.

| Signal | Diagnosis | Action |
|--------|-----------|--------|
| Skill never triggers | Undertriggering | Broaden description; add synonyms and trigger phrases |
| Skill triggers for wrong queries | Overtriggering | Narrow description; add qualifying context |
| Claude reads SKILL.md but ignores steps | Instructions too verbose or buried | Shorten; move critical steps to top; use numbered lists |
| Claude re-generates code that a script handles | Script not discovered | Add explicit "Run `scripts/X.py`" instructions |
| Output quality varies between runs | Insufficient constraints | Add templates or examples; reduce degrees of freedom |
| Claude loads all reference files | Poor progressive disclosure | Add clear "Read X only when Y" conditions |
| Works on Opus but fails on Haiku | Insufficient guidance for smaller models | Add more explicit steps; reduce ambiguity |
| Works on Haiku but over-explains on Opus | Too much hand-holding | Move detailed guidance to reference files |
| Users report unexpected behavior | Missing edge case handling | Add the scenario to SKILL.md or scripts |
| Skill works but feels slow | Too much context loaded | Split content; make references more granular |
