#!/bin/bash
# Validate Gemini API key is available before podcast-generator commands
#
# This hook runs before Bash tool use to ensure the Gemini API key is configured.
# It only validates when the command contains Gemini/podcast-generator references.
# Checks both scripts/credentials.json and $GEMINI_API_KEY env var.

# Gracefully allow if jq is not available
if ! command -v jq &> /dev/null; then
    echo '{"decision": "allow"}'
    exit 0
fi

# Read the tool input from stdin
INPUT=$(cat)

# Extract the command being run
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Only validate if the command involves Gemini/podcast-generator
if echo "$COMMAND" | grep -qE "generate_audio|extract_sources|GEMINI_API_KEY|google.*genai"; then
  # Check credentials file first
  SCRIPT_DIR="$(cd "$(dirname "$0")/../skills/podcast-generator" && pwd)/scripts"
  CREDS_FILE="$SCRIPT_DIR/credentials.json"
  if [ -f "$CREDS_FILE" ]; then
    KEY=$(jq -r '.gemini_api_key // empty' "$CREDS_FILE" 2>/dev/null)
    if [ -n "$KEY" ] && [ "$KEY" != "YOUR_GEMINI_API_KEY_HERE" ]; then
      echo '{"decision": "allow"}'
      exit 0
    fi
  fi

  # Check env var
  if [ -n "$GEMINI_API_KEY" ]; then
    echo '{"decision": "allow"}'
    exit 0
  fi

  # No key found
  echo '{"decision": "block", "message": "Gemini API key not found. Place credentials.json in podcast-generator/scripts/ directory or set GEMINI_API_KEY in ~/.zshrc. Get a key at https://aistudio.google.com/apikey"}'
  exit 0
fi

# Allow the action to proceed
echo '{"decision": "allow"}'
