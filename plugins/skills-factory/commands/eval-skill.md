---
description: Run evaluation suite against a skill to test triggering and quality
---

Run the skill-eval evaluation pipeline against a skill.

**Usage:** `/eval-skill [skill-path]`

If `$ARGUMENTS` is provided, use it as the skill path. Otherwise, ask the user which skill to evaluate.

## Steps

1. Locate the skill directory (resolve `$ARGUMENTS` or ask)
2. Check for `.skill-eval/` workspace — if missing, run `eval_scaffold.py` to bootstrap evals
3. Run `eval_workspace.py run <skill-path>` to execute the full eval pipeline
4. Display results summary (pass rates, regressions)
5. Ask if the user wants to open the interactive HTML viewer (`generate_review.py`)
