---
description: Validate, evaluate, quality-check, and package a skill for distribution
---

Full ship pipeline: validate, evaluate, quality-gate, and package a skill.

**Usage:** `/ship-skill [skill-path]`

If `$ARGUMENTS` is provided, use it as the skill path. Otherwise, ask the user which skill to ship.

## Pipeline

1. **Validate** — Run `skills-ref validate <skill-path>` (or `quick_validate.py` as fallback). Stop on failure.
2. **Eval** — Run the eval suite via `eval_workspace.py run`. All Tier 1 checks must pass. 80%+ Tier 2 assertions must pass. Stop on failure.
3. **Quality gate** — Check:
   - SKILL.md under 500 lines
   - No TODO markers in content
   - All referenced files exist
   - Token budget under threshold (`token_budget.py`)
   - Description under 1024 characters
4. **Package** — Run `package_skill.py <skill-dir>` to generate the `.skill` file
5. **Summary card** — Display: skill name, eval pass rate, token budget, package size, distribution readiness

If any step fails, stop and report the issue with actionable guidance.
