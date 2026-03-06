# Output Patterns

Patterns for producing consistent, high-quality output from skills.

## Template Pattern

Provide templates for output format. Match strictness to requirements.

**For strict requirements** (API responses, data formats):
```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
[One-paragraph overview]
## Key findings
- Finding 1 with supporting data
## Recommendations
1. Specific actionable recommendation
```

**For flexible guidance** (when adaptation is useful):
```markdown
## Report structure
Here is a sensible default, but adapt as needed:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

## Examples Pattern

When output quality depends on seeing examples, provide input/output pairs:

````markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output:
```
feat(auth): implement JWT-based authentication
Add login endpoint and token validation middleware
```

**Example 2:**
Input: Fixed bug where dates displayed incorrectly
Output:
```
fix(reports): correct date formatting in timezone conversion
```
````

Examples teach style and detail level more effectively than descriptions alone.

## Visual Output Pattern

For skills that produce results users need to visually inspect (reports, dashboards, data viz):

```markdown
## Reviewing Results
1. Generate a self-contained HTML file with embedded CSS and data
2. Save to /tmp/<skill-name>-output.html
3. Open in browser: `open /tmp/<skill-name>-output.html`
4. Wait for user feedback before proceeding

For headless environments, use --static <path> to write HTML without serving.
```

This pattern works across environments: Claude Code opens a browser, Cowork serves a static file, Claude.ai presents inline.

## Structured Data Pattern

For skills producing JSON, YAML, or other structured output:

```markdown
## Output Schema
Write results as JSON matching this structure:
{
  "status": "success" | "failure",
  "items": [
    { "name": "string", "value": 0, "metadata": {} }
  ],
  "summary": "One-line description of results"
}
```

For strict schemas, include validation: "Run `python3 -c 'import json; json.load(open(\"output.json\"))'` to verify."
