---
name: build-skill-zips
description: Build standalone .skill files for Claude.ai users
allowed-tools: Bash
license: MIT
compatibility: bash, zip utility
---
Run the build script to generate standalone `.skill` files that Claude.ai users can upload via Settings > Capabilities.

$ARGUMENTS

If arguments are provided, treat them as a skill name filter (e.g., "epub-creator" to build only that skill). Otherwise build all skills.

## Steps

1. **Run build script:**
   ```bash
   bash scripts/build-skill-zips.sh $ARGUMENTS
   ```

2. **Report results** with the list of generated `.skill` files and their sizes.
