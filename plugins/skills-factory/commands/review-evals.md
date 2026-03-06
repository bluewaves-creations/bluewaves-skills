---
description: Generate and open interactive HTML viewer for skill evaluation results
---

Open the interactive HTML eval viewer for a skill's evaluation results.

**Usage:** `/review-evals [skill-path]`

If `$ARGUMENTS` is provided, use it as the skill path. Otherwise, ask the user which skill to review.

## Steps

1. Locate the skill directory and its `.skill-eval/` workspace
2. Find the latest run directory (or ask which run to review)
3. Run `generate_review.py <workspace> --skill-name <name>`
4. Open the HTML viewer in the browser (or use `--static <path>` for headless environments)
5. Wait for user feedback from the viewer
