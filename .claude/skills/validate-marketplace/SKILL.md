---
name: validate-marketplace
description: Validate the entire marketplace — skills, plugins, marketplace.json, cross-consistency, and skill quality
allowed-tools: Bash
license: MIT
compatibility: Python 3.8+. skills-ref library recommended.
---
Run the comprehensive marketplace validator that checks all five layers:
skills (via skills-ref), plugin.json files, marketplace.json structure,
cross-consistency, and skill-shaper quality best practices.

$ARGUMENTS

## Steps

1. **Run validation:**
   ```bash
   python3 scripts/validate_marketplace.py
   ```

2. **Report results** with pass/fail status for each validation layer.
