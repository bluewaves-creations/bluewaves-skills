# .eval.yaml Format

Specification and examples for the `.eval.yaml` test case format used by skill-eval.

---

## Structure

```yaml
name: descriptive-name              # Identifier used in reports
query: "Realistic user prompt"      # What a user would actually type
should_trigger: true                # Whether the skill should activate

checks:                             # Tier 1: programmatic, zero tokens
  - type: file_exists
    target: "output.pdf"

assertions:                         # Tier 2: agent-graded, if Tier 1 passes
  - "The PDF contains a table of contents on page 2"
```

---

## Tier 1 Check Types

| Type | Parameters | Description |
|------|-----------|-------------|
| `file_exists` | `target` (glob) | File matching pattern exists in outputs/ |
| `regex` | `target`, `pattern` | File contents match regex |
| `json_valid` | `target` | File contains valid JSON |
| `yaml_valid` | `target` | File contains valid YAML |
| `exit_code` | `expected` (int) | Process exit code matches |
| `contains` | `target`, `expected` | File contains exact text |
| `not_contains` | `target`, `expected` | File does NOT contain text |
| `line_count_range` | `target`, `min`, `max` | File line count within range |
| `file_size_range` | `target`, `min`, `max` | File size (bytes) within range |

---

## Tier 2 Assertion Guidelines

Assertions are natural language descriptions evaluated by the grader agent:

**Good assertions:**
- "The output table has exactly 5 columns: Name, Date, Amount, Status, Notes"
- "The generated script handles the empty input case without crashing"
- "The summary correctly identifies all 3 key findings from the source document"

**Bad assertions:**
- "The output is good" (subjective, not verifiable)
- "A file was created" (use Tier 1 `file_exists` instead)
- "The output is correct" (too vague — correct how?)

---

## Category-Specific Check Recommendations

### Document creation skills
```yaml
checks:
  - type: file_exists
    target: "*.pdf"     # or *.docx, *.epub, etc.
  - type: file_size_range
    target: "output.pdf"
    min: 1000           # Not empty
  - type: line_count_range
    target: "output.md"
    min: 10
```

### Workflow / automation skills
```yaml
checks:
  - type: exit_code
    expected: 0
  - type: file_exists
    target: "result.*"
  - type: not_contains
    target: "log.txt"
    expected: "ERROR"
```

### Data processing skills
```yaml
checks:
  - type: json_valid
    target: "output.json"
  - type: contains
    target: "output.json"
    expected: '"status"'
  - type: regex
    target: "output.csv"
    pattern: "^\\w+,\\w+,"    # Has header row
```

---

## Negative Eval Patterns

Negative evals (`should_trigger: false`) test that the skill does NOT activate for unrelated queries.

**Good negative evals** — near-misses that share keywords:
```yaml
name: unrelated-pdf-read
query: "Can you read this PDF and tell me what's in it?"
should_trigger: false
# Near-miss: mentions PDF but is a simple read task, not a skill-worthy operation
```

**Bad negative evals** — obviously irrelevant:
```yaml
name: fibonacci
query: "Write a fibonacci function"
should_trigger: false
# Too easy: doesn't test anything about the skill's trigger boundary
```

---

## Complete Example

```yaml
name: quarterly-report-generation
query: "Generate a Q4 2025 financial report from the data in quarterly_data.csv. Include charts for revenue trends and a summary table."
should_trigger: true
checks:
  - type: file_exists
    target: "*.pdf"
  - type: file_size_range
    target: "*.pdf"
    min: 5000
  - type: not_contains
    target: "*.pdf"
    expected: "TODO"
assertions:
  - "The report includes a revenue trend chart covering Q1-Q4 2025"
  - "The summary table shows revenue, costs, and profit margin for each quarter"
  - "The report has a professional cover page with the title 'Q4 2025 Financial Report'"
```
