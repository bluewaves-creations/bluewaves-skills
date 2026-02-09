#!/bin/bash
# Validate Python dependencies for docs-factory PDF rendering

# Gracefully allow if jq is not available
if ! command -v jq &> /dev/null; then
    echo '{"decision": "allow"}'
    exit 0
fi

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

# Only validate for commands that run pdf-factory scripts (sandboxed by path)
# Matches: python3 /any/path/pdf-factory/scripts/render.py, compose.py, validate_output.py
# Does NOT match: other plugins' scripts, generic python commands
if [[ "$COMMAND" =~ python.*docs-factory/skills/pdf-factory/scripts/.*\.py ]]; then

    # Skip package validation for install_deps.py (it installs them)
    if [[ "$COMMAND" =~ install_deps\.py ]]; then
        # Still check Python is available
        if ! command -v python3 &> /dev/null; then
            echo '{"decision": "block", "message": "Python 3 required. Install from python.org or via: brew install python3"}'
            exit 0
        fi
        echo '{"decision": "allow"}'
        exit 0
    fi

    # Extract venv python from command if invoked directly
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

    # Check required packages
    MISSING=""
    "$PYTHON" -c "import xhtml2pdf" 2>/dev/null || MISSING="$MISSING xhtml2pdf"
    "$PYTHON" -c "import reportlab" 2>/dev/null || MISSING="$MISSING reportlab"
    "$PYTHON" -c "import pypdf" 2>/dev/null || MISSING="$MISSING pypdf"
    "$PYTHON" -c "import pyhanko" 2>/dev/null || MISSING="$MISSING pyhanko"
    "$PYTHON" -c "import markdown" 2>/dev/null || MISSING="$MISSING markdown"
    "$PYTHON" -c "import lxml" 2>/dev/null || MISSING="$MISSING lxml"
    "$PYTHON" -c "import PIL" 2>/dev/null || MISSING="$MISSING pillow"
    "$PYTHON" -c "import html5lib" 2>/dev/null || MISSING="$MISSING html5lib"
    "$PYTHON" -c "import cssselect2" 2>/dev/null || MISSING="$MISSING cssselect2"

    if [ -n "$MISSING" ]; then
        echo "{\"decision\": \"block\", \"message\": \"Missing Python packages:$MISSING\n\nInstall with:\n  /docs-factory:install-deps\n\nOr manually:\n  pip install$MISSING\"}"
        exit 0
    fi
fi

echo '{"decision": "allow"}'
