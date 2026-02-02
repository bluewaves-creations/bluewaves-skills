---
description: Build standalone skill ZIP files for Claude.ai users
---
Run the build script to generate standalone skill ZIP files that Claude.ai users can upload via Settings > Capabilities.

$ARGUMENTS

If arguments are provided, treat them as a skill name filter (e.g., "gemini-image" to build only that skill). Otherwise build all skills.

Execute: `bash scripts/build-skill-zips.sh $ARGUMENTS`
