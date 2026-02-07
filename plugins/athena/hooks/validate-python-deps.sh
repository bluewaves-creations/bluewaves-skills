#!/bin/bash
# Validate Python availability for athena plugin scripts

# Gracefully allow if jq is not available
if ! command -v jq &> /dev/null; then
    echo '{"decision": "allow"}'
    exit 0
fi

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

# Only validate for commands that actually RUN athena Python scripts
if [[ "$COMMAND" =~ python.*athena.*\.py|create_athena_package\.py|validate_athena_package\.py ]]; then
    # Extract venv python from command if invoked directly (e.g. /path/.venv/bin/python)
    VENV_PYTHON=$(echo "$COMMAND" | grep -oE '/[^ ]*venv[^ ]*/bin/python[3]?' | head -1)
    if [ -n "$VENV_PYTHON" ] && [ -x "$VENV_PYTHON" ]; then
        PYTHON="$VENV_PYTHON"
    elif [ -n "$VIRTUAL_ENV" ] && [ -x "$VIRTUAL_ENV/bin/python3" ]; then
        PYTHON="$VIRTUAL_ENV/bin/python3"
    else
        PYTHON="python3"
    fi

    # Check Python
    if ! command -v "$PYTHON" &> /dev/null; then
        echo '{"decision": "block", "message": "Python 3 required. Install from python.org or via: brew install python3"}'
        exit 0
    fi

    # Check Python version (3.8+)
    PY_VERSION=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

    if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 8 ]); then
        echo "{\"decision\": \"block\", \"message\": \"Python 3.8+ required. Current version: $PY_VERSION\"}"
        exit 0
    fi

    # No package import checks needed — athena scripts use stdlib only
fi

echo '{"decision": "allow"}'
