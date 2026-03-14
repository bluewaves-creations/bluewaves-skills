---
name: package-skill
description: Package a skill folder into a distributable .skill ZIP file
allowed-tools: Bash
license: MIT
compatibility: Python 3.8+ (stdlib only)
---
Package a validated skill into a distributable `.skill` ZIP file.

$ARGUMENTS

Arguments should be: `<skill-folder> [output-directory]`. If no arguments are provided, ask the user for the skill path.

## Steps

1. **Locate the script:**
   ```bash
   SCRIPT="${SKILL_ROOT}/../skill-shaper/scripts/package_skill.py"
   ```

2. **Run package_skill.py:**
   ```bash
   python3 "$SCRIPT" $ARGUMENTS
   ```

3. **Report results:** Show the path to the created `.skill` file and its size. If packaging failed (e.g., validation errors), report the issues.
