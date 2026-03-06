# Testing and Debugging Skills

For automated evaluation, benchmarking, and description optimization, use the **skill-eval** skill. This reference covers quick manual testing and common debugging patterns.

## Two-Tier Testing Philosophy

**Tier 1 (programmatic):** Zero token cost. Check file existence, content patterns, format validity, exit codes. Catches structural failures instantly.

**Tier 2 (agent-graded):** Only runs if Tier 1 passes. Evaluates subjective quality, completeness, correctness. Uses grading agent with evidence-based PASS/FAIL.

This saves 60-80% of grading tokens by filtering obvious failures before agent evaluation.

## Quick Manual Testing

Before automated evals, do a sanity check:

### Trigger Testing
- Try 5+ paraphrased queries — does the skill activate?
- Try 3+ unrelated queries — does it stay quiet?
- Test edge cases: abbreviations, synonyms, indirect references

### Functional Testing
- Run the primary workflow end-to-end with realistic inputs
- Test at least one edge case (empty input, large input, unusual format)
- Test error conditions (missing dependencies, invalid files)

### Performance Comparison
- Run 3+ tasks WITHOUT the skill → document output quality
- Run same tasks WITH the skill → compare
- If the skill doesn't improve at least one metric, reconsider

## Description Testing Methodology

The description is the primary triggering mechanism. Test it specifically:

1. **Generate 20 queries** — 10 should-trigger, 10 should-not-trigger
2. **Focus on near-misses** — queries that share keywords but need different tools
3. **Use realistic language** — file paths, context, typos, casual speech
4. **Run with run_eval.py** — 3 runs per query for reliable trigger rates

Bad negative: "Write a fibonacci function" (too easy, tests nothing)
Good negative: "Can you read this PDF and tell me what's in it?" (shares keywords, different intent)

## Baseline Comparison

Always compare with-skill vs without-skill. This is the only way to measure whether the skill adds value. A skill that doesn't improve output quality needs restructuring.

## Regression Testing

Pin a known-good baseline with `eval_workspace.py pin`. After changes, run `eval_workspace.py regress` to detect PASS→FAIL transitions. Regressions are flagged prominently.

## Debugging Common Problems

### Undertriggering (skill doesn't activate)

| Cause | Fix |
|-------|-----|
| Description too narrow | Add synonyms, related terms, alternative phrasings |
| Missing key terms | Include words users actually say |
| Description too technical | Add plain-language triggers |
| Competing skill | Make description more specific |

### Overtriggering (activates for wrong queries)

| Cause | Fix |
|-------|-----|
| Description too broad | Narrow with specific qualifiers |
| Generic keywords | Replace "documents" with "PDF documents" |

### Instructions Not Followed

| Cause | Fix |
|-------|-----|
| SKILL.md too verbose | Cut ruthlessly |
| Critical info buried | Move to top of sections |
| Ambiguous wording | Use imperative form with explicit steps |
| Too many options | Provide default with escape hatch |

### Heavy Context

| Cause | Fix |
|-------|-----|
| SKILL.md too long | Split into references; stay under 500 lines |
| Loading unnecessary refs | Add "read only when..." conditions |
| Large scripts in context | Design scripts to execute, not be read |

Run `token_budget.py` to measure actual cost per section.

## Iteration Signals

| Signal | Diagnosis | Action |
|--------|-----------|--------|
| Never triggers | Undertriggering | Broaden description |
| Triggers for wrong queries | Overtriggering | Narrow description |
| Reads SKILL.md but ignores steps | Too verbose | Shorten; move critical steps to top |
| Re-generates code a script handles | Script not found | Add explicit "Run scripts/X.py" |
| Output varies between runs | Insufficient constraints | Add templates or examples |
| Loads all reference files | Poor progressive disclosure | Add "Read X only when Y" conditions |
| Works on Opus, fails on Haiku | Insufficient guidance | Add more explicit steps |
