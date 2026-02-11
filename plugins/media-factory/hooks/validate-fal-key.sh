#!/bin/bash
# Validate fal.ai API key is available before API calls
#
# This hook runs before Bash tool use to ensure the API key is configured.
# It only validates when the command contains fal.ai references.
# Checks both $FAL_KEY env var and credentials.json file.

# Gracefully allow if jq is not available
if ! command -v jq &> /dev/null; then
    echo '{"decision": "allow"}'
    exit 0
fi

# Read the tool input from stdin
INPUT=$(cat)

# Extract the command being run
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Only validate if the command involves fal.ai
if echo "$COMMAND" | grep -qE "fal[._](run|ai|client|generate)|FAL_KEY"; then
  # Check credentials file first
  SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)/scripts"
  CREDS_FILE="$SCRIPT_DIR/credentials.json"
  if [ -f "$CREDS_FILE" ]; then
    KEY=$(jq -r '.api_key // empty' "$CREDS_FILE" 2>/dev/null)
    if [ -n "$KEY" ] && [ "$KEY" != "USER_KEY_HERE" ]; then
      echo '{"decision": "allow"}'
      exit 0
    fi
  fi

  # Check env var
  if [ -n "$FAL_KEY" ]; then
    echo '{"decision": "allow"}'
    exit 0
  fi

  # No key found
  echo '{"decision": "block", "message": "fal.ai API key not found. Place credentials.json in scripts/ directory or set FAL_KEY in ~/.zshrc. Run /media-factory:check-fal-key for help."}'
  exit 0
fi

# Allow the action to proceed
echo '{"decision": "allow"}'
