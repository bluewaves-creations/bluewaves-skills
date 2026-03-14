---
name: validate-skills
description: Validate skill SKILL.md files using the skills-ref specification
allowed-tools: Bash
license: MIT
compatibility: skills-ref library (deps/agentskills/skills-ref/)
---
Run the marketplace skill validation script against all skills (or a single skill if specified).

$ARGUMENTS

If arguments are provided, treat them as a skill name filter (e.g., "skill-shaper" to validate only that skill). Otherwise validate all skills.

## Steps

1. **Run validation:**
   ```bash
   bash scripts/validate-skills.sh $ARGUMENTS
   ```

2. **Report results** with pass/fail status for each validated skill.
