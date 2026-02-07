---
description: Validate a .athena package against the import specification
---
Validate a `.athena` package or staging directory against the Athena import specification.

$ARGUMENTS

The argument should be a file path to a `.athena` file or a staging directory.

## Steps

1. **Validate argument:** Ensure a path was provided and exists.

2. **Run validation:**
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/athena-package/scripts/validate_athena_package.py "$ARGUMENTS"
   ```

3. **Report results:** If validation passes, confirm the package is ready for import. If errors are found, list them with fix guidance based on the error messages.
