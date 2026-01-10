#!/bin/bash
# Validate Python dependencies for epub-generator

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

# Only validate for epub-related commands
if [[ "$COMMAND" =~ (ebooklib|epub|create_epub|EpubBook|markdown_to_epub|generate_epub) ]]; then
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo '{"decision": "block", "message": "Python 3 required. Install from python.org or via: brew install python3"}'
        exit 0
    fi

    # Check Python version (3.8+)
    PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

    if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 8 ]); then
        echo "{\"decision\": \"block\", \"message\": \"Python 3.8+ required. Current version: $PY_VERSION\"}"
        exit 0
    fi

    # Check required packages
    MISSING=""
    python3 -c "import ebooklib" 2>/dev/null || MISSING="$MISSING ebooklib"
    python3 -c "import markdown" 2>/dev/null || MISSING="$MISSING markdown"
    python3 -c "import PIL" 2>/dev/null || MISSING="$MISSING Pillow"
    python3 -c "import bs4" 2>/dev/null || MISSING="$MISSING beautifulsoup4"
    python3 -c "import lxml" 2>/dev/null || MISSING="$MISSING lxml"
    python3 -c "import yaml" 2>/dev/null || MISSING="$MISSING PyYAML"

    if [ -n "$MISSING" ]; then
        echo "{\"decision\": \"block\", \"message\": \"Missing Python packages:$MISSING\n\nInstall with:\n  uv pip install$MISSING\n\nOr with pip:\n  pip install$MISSING\"}"
        exit 0
    fi
fi

echo '{"decision": "allow"}'
