---
description: Scaffold a new skill directory from template using init_skill.py
---
Create a new skill from the built-in template.

$ARGUMENTS

Arguments should be: `<skill-name> --path <directory>`

If no arguments are provided, ask the user for a skill name and target path.

## Steps

1. **Locate the script:**
   ```bash
   SCRIPT="${CLAUDE_PLUGIN_ROOT}/skills/skill-shaper/scripts/init_skill.py"
   ```

2. **Run init_skill.py:**
   ```bash
   python3 "$SCRIPT" $ARGUMENTS
   ```

3. **Report results:** Show the created directory structure and remind the user to edit the `SKILL.md` frontmatter (name, description) and fill in the skill content.
