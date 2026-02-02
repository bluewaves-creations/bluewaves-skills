---
description: Validate a skill folder using quick_validate.py
---
Validate a skill directory to check that its SKILL.md has correct frontmatter and structure.

$ARGUMENTS

Arguments should be the path to a skill folder containing a SKILL.md file. If no arguments are provided, ask the user for the skill path.

## Steps

1. **Locate the script:**
   ```bash
   SCRIPT="${CLAUDE_PLUGIN_ROOT}/skills/skill-creator/scripts/quick_validate.py"
   ```

2. **Run quick_validate.py:**
   ```bash
   python3 "$SCRIPT" $ARGUMENTS
   ```

3. **Report results:** Show validation outcome and any issues found. If validation fails, provide specific guidance on how to fix each issue.
