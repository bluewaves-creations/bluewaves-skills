# JSON Schemas

All JSON schemas used by skill-eval scripts. Field names are exact — viewers and scripts depend on them.

---

## .eval.yaml

Defines a single test case. Located in `.skill-eval/evals/`.

```yaml
name: descriptive-eval-name
query: "Realistic user prompt"
should_trigger: true
checks:                      # Tier 1 — programmatic, zero tokens
  - type: file_exists
    target: "output.pdf"
  - type: contains
    target: "output.txt"
    expected: "Summary"
  - type: regex
    target: "output.txt"
    pattern: "^# "
assertions:                  # Tier 2 — agent-graded, only if Tier 1 passes
  - "Output contains a valid table of contents"
  - "The generated PDF has correct page numbering"
```

**Fields:**
- `name`: Descriptive identifier for the eval (used in reports)
- `query`: The prompt to test (realistic user language)
- `should_trigger`: Whether the skill should activate for this query
- `checks[]`: Tier 1 programmatic checks (see eval-format.md for all types)
  - `type`: Check type (file_exists, regex, json_valid, yaml_valid, exit_code, contains, not_contains, line_count_range, file_size_range)
  - `target`: File to check (relative to outputs/)
  - `pattern`/`expected`/`min`/`max`: Type-specific parameters
- `assertions[]`: Tier 2 agent-graded assertions (string descriptions)

---

## grading.json

Output from eval_grader.py. Located at `runs/NNN/grading.json`.

```json
{
  "expectations": [
    {
      "text": "[Check] file_exists: output.pdf",
      "passed": true,
      "evidence": "Found: ['output.pdf']",
      "tier": 1
    },
    {
      "text": "Output contains a valid table of contents",
      "passed": true,
      "evidence": "Found ToC on page 2 with 5 entries",
      "tier": 2
    }
  ],
  "summary": {
    "passed": 4,
    "failed": 1,
    "total": 5,
    "pass_rate": 0.80,
    "tier1_passed": true,
    "tier1_count": 3
  },
  "execution_metrics": {
    "tool_calls": { "Read": 5, "Write": 2, "Bash": 8 },
    "total_tool_calls": 15,
    "total_steps": 6,
    "files_created": ["output.pdf", "metadata.json"],
    "errors_encountered": 0,
    "output_chars": 12450,
    "transcript_chars": 3200,
    "user_notes": []
  },
  "timing": {
    "total_tokens": 84852,
    "duration_ms": 23332,
    "total_duration_seconds": 23.3,
    "executor_start": "2026-01-15T10:30:00Z",
    "executor_end": "2026-01-15T10:32:45Z",
    "executor_duration_seconds": 165.0,
    "grader_start": "2026-01-15T10:32:46Z",
    "grader_end": "2026-01-15T10:33:12Z",
    "grader_duration_seconds": 26.0
  },
  "claims": [
    {
      "claim": "The form has 12 fillable fields",
      "type": "factual",
      "verified": true,
      "evidence": "Counted 12 fields in field_info.json"
    }
  ],
  "user_notes_summary": {
    "uncertainties": ["Used 2023 data, may be stale"],
    "needs_review": [],
    "workarounds": ["Fell back to text overlay for non-fillable fields"]
  },
  "eval_feedback": {
    "suggestions": [
      {
        "assertion": "Output includes name",
        "reason": "A hallucinated document would also pass"
      }
    ],
    "overall": "Assertions check presence but not correctness."
  }
}
```

**Key fields:**
- `expectations[].text`: The expectation text (prefixed with `[Check]` for Tier 1)
- `expectations[].passed`: Boolean (or null for pending Tier 2)
- `expectations[].evidence`: Quoted evidence supporting verdict
- `expectations[].tier`: 1 (programmatic) or 2 (agent-graded)
- `summary.tier1_passed`: Whether all Tier 1 checks passed
- `claims[]`: Implicit claims extracted and verified from output
- `user_notes_summary`: Issues flagged by the executor
- `eval_feedback`: Grader's critique of eval quality

---

## metrics.json

Execution metrics captured during a run. Located at `runs/NNN/metrics.json`.

```json
{
  "tool_calls": { "Read": 5, "Write": 2, "Bash": 8, "Edit": 1 },
  "total_tool_calls": 16,
  "total_steps": 6,
  "files_created": ["output.pdf", "metadata.json"],
  "errors_encountered": 0,
  "output_chars": 12450,
  "transcript_chars": 3200,
  "user_notes": ["Used cached data for performance"]
}
```

---

## timing.json

Timing data captured from task notifications. Located at `runs/NNN/timing.json`.

**Critical:** `total_tokens` and `duration_ms` come from task completion notifications and are NOT persisted elsewhere. Capture immediately.

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3,
  "executor_start": "2026-01-15T10:30:00Z",
  "executor_end": "2026-01-15T10:32:45Z",
  "executor_duration_seconds": 165.0,
  "grader_start": "2026-01-15T10:32:46Z",
  "grader_end": "2026-01-15T10:33:12Z",
  "grader_duration_seconds": 26.0
}
```

---

## benchmark.json

Aggregated statistics from aggregate_benchmark.py. Located at benchmark directory root.

```json
{
  "metadata": {
    "skill_name": "pdf-processor",
    "timestamp": "2026-01-15T10:30:00Z",
    "evals_run": ["form-fill", "table-extract", "merge-pdfs"],
    "total_runs": 18
  },
  "runs": [
    {
      "eval_name": "form-fill",
      "configuration": "with_skill",
      "run_number": 1,
      "result": {
        "pass_rate": 0.85,
        "passed": 6,
        "failed": 1,
        "total": 7,
        "time_seconds": 42.5,
        "tokens": 3800,
        "tool_calls": 18,
        "errors": 0
      },
      "expectations": [
        { "text": "...", "passed": true, "evidence": "..." }
      ]
    }
  ],
  "run_summary": {
    "with_skill": {
      "pass_rate": { "mean": 0.85, "stddev": 0.05, "min": 0.80, "max": 0.90 },
      "time_seconds": { "mean": 45.0, "stddev": 12.0, "min": 32.0, "max": 58.0 },
      "tokens": { "mean": 3800, "stddev": 400, "min": 3200, "max": 4100 }
    },
    "without_skill": {
      "pass_rate": { "mean": 0.35, "stddev": 0.08, "min": 0.28, "max": 0.45 },
      "time_seconds": { "mean": 32.0, "stddev": 8.0, "min": 24.0, "max": 42.0 },
      "tokens": { "mean": 2100, "stddev": 300, "min": 1800, "max": 2500 }
    },
    "delta": {
      "pass_rate": "+0.50",
      "time_seconds": "+13.0",
      "tokens": "+1700"
    }
  },
  "notes": [
    "Assertion 'Output is a PDF' passes 100% in both configs - non-discriminating",
    "Eval 3 shows high variance (50% +/- 40%) - may be flaky"
  ]
}
```

**Important:** The viewer reads `configuration` (not `config`), `result.pass_rate` (nested, not top-level), and `run_summary.delta`. Match these exactly.

---

## comparison.json

Output from blind comparator agent. Located at grading directory.

```json
{
  "winner": "A",
  "reasoning": "Output A provides complete solution with proper formatting.",
  "rubric": {
    "A": {
      "content": { "correctness": 5, "completeness": 5, "accuracy": 4 },
      "structure": { "organization": 4, "formatting": 5, "usability": 4 },
      "content_score": 4.7,
      "structure_score": 4.3,
      "overall_score": 9.0
    },
    "B": { "...": "same structure" }
  },
  "output_quality": {
    "A": { "score": 9, "strengths": ["..."], "weaknesses": ["..."] },
    "B": { "score": 5, "strengths": ["..."], "weaknesses": ["..."] }
  },
  "expectation_results": {
    "A": { "passed": 4, "total": 5, "pass_rate": 0.80, "details": [] },
    "B": { "passed": 3, "total": 5, "pass_rate": 0.60, "details": [] }
  }
}
```

---

## analysis.json

Output from post-hoc analyzer agent.

```json
{
  "comparison_summary": {
    "winner": "A",
    "winner_skill": "path/to/winner/skill",
    "loser_skill": "path/to/loser/skill",
    "comparator_reasoning": "Brief summary"
  },
  "winner_strengths": ["Clear step-by-step instructions", "Included validation script"],
  "loser_weaknesses": ["Vague instructions", "No validation"],
  "improvement_suggestions": [
    {
      "priority": "high",
      "category": "instructions",
      "suggestion": "Replace vague language with explicit steps",
      "expected_impact": "Eliminates ambiguity"
    }
  ],
  "transcript_insights": {
    "winner_execution_pattern": "Read skill -> Followed 5-step process -> Validated",
    "loser_execution_pattern": "Read skill -> Unclear -> Tried 3 methods"
  }
}
```

---

## manifest.json

Workspace metadata. Located at `.skill-eval/manifest.json`.

```json
{
  "skill_name": "my-skill",
  "created": "2026-01-15T10:30:00Z",
  "runs": [
    {
      "id": "001",
      "timestamp": "2026-01-15T10:35:00Z",
      "skill_hash": "a1b2c3d4e5f6",
      "summary": { "passed": 4, "total": 5, "pass_rate": 0.80 }
    }
  ],
  "pinned_baseline": "001"
}
```
