#!/bin/bash
# Validate FAL_KEY environment variable is set before fal.ai API calls
#
# This hook runs before Bash tool use to ensure the API key is configured.
# It only validates when the command contains fal.ai references.

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
if echo "$COMMAND" | grep -qE "fal[._](run|ai|client)|FAL_KEY"; then
  if [ -z "$FAL_KEY" ]; then
    # Output JSON to block the action with a helpful message
    echo '{"decision": "block", "message": "FAL_KEY environment variable is not set. Please set it in ~/.zshrc or export it: export FAL_KEY=your_key"}'
    exit 0
  fi
fi

# Allow the action to proceed
echo '{"decision": "allow"}'
