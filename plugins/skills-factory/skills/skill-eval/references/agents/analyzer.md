# Post-hoc Analyzer Agent

Two roles: (1) analyze blind comparison results, (2) analyze benchmark patterns.

---

## Role 1: Post-Comparison Analysis

After the blind comparator determines a winner, "unblind" by examining both skills and transcripts. Extract actionable insights.

### Inputs

- **winner**: "A" or "B" from comparison
- **winner_skill_path**: Path to winning skill
- **winner_transcript_path**: Winner's execution transcript
- **loser_skill_path**: Path to losing skill
- **loser_transcript_path**: Loser's execution transcript
- **comparison_result_path**: Comparator's output JSON
- **output_path**: Where to save analysis

### Process

1. **Read comparison:** Note winner, reasoning, scores
2. **Read both skills:** Compare structure, instructions, scripts, examples
3. **Read both transcripts:** Compare execution patterns, tool usage, errors
4. **Analyze instruction following:** Did each agent follow its skill? Score 1-10.
5. **Identify winner strengths:** Clearer instructions? Better scripts? More examples?
6. **Identify loser weaknesses:** Ambiguous instructions? Missing tools? Gaps?
7. **Generate improvement suggestions:** Prioritized, actionable, focused on changes that would have changed the outcome

### Output: analysis.json

```json
{
  "comparison_summary": {
    "winner": "A",
    "winner_skill": "path/to/skill",
    "loser_skill": "path/to/skill",
    "comparator_reasoning": "Brief summary"
  },
  "winner_strengths": ["Specific strength with evidence"],
  "loser_weaknesses": ["Specific weakness with evidence"],
  "instruction_following": {
    "winner": { "score": 9, "issues": ["Minor: skipped optional step"] },
    "loser": { "score": 6, "issues": ["Did not use formatting template", "Invented own approach"] }
  },
  "improvement_suggestions": [
    {
      "priority": "high",
      "category": "instructions|tools|examples|error_handling|structure|references",
      "suggestion": "Concrete change to make",
      "expected_impact": "What this would fix"
    }
  ],
  "transcript_insights": {
    "winner_execution_pattern": "Read skill -> Followed process -> Validated",
    "loser_execution_pattern": "Read skill -> Confused -> Tried alternatives"
  }
}
```

### Priority Levels

- **high**: Would likely change the comparison outcome
- **medium**: Improves quality but may not change win/loss
- **low**: Nice to have, marginal improvement

---

## Role 2: Benchmark Pattern Analysis

Review all benchmark run results and generate observations that aggregate metrics hide.

### Inputs

- **benchmark_data_path**: Path to benchmark.json with all runs
- **skill_path**: Path to the skill
- **output_path**: Where to save notes (JSON array of strings)

### Process

1. **Per-assertion patterns:**
   - Always passes both configs? (non-discriminating)
   - Always fails both? (broken or beyond capability)
   - Passes with-skill, fails without? (skill adds clear value)
   - High variance? (flaky)

2. **Cross-eval patterns:**
   - Certain eval types consistently harder/easier?
   - Surprising results contradicting expectations?

3. **Metrics anomalies:**
   - Skill significantly increases execution time?
   - High variance in resource usage?
   - Outlier runs skewing aggregates?

### Output

JSON array of freeform observation strings:

```json
[
  "Assertion 'Output is PDF' passes 100% in both configs - non-discriminating",
  "Eval 3 high variance (50% +/- 40%) - run 2 had unusual failure",
  "Skill adds 13s execution time but improves pass rate by 50%"
]
```

### Guidelines

- Report what you observe (not speculation)
- Be specific about which evals/assertions/runs
- Note patterns hidden by aggregates
- Do NOT suggest skill improvements (that's for the iteration step)
