#!/bin/bash
# Validate Xcode command line tools are installed before Swift-related commands
#
# This hook runs before Bash tool use to ensure Xcode tools are available.
# It only validates when the command involves Swift development.

# Read the tool input from stdin
INPUT=$(cat)

# Extract the command being run
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

# Only validate for Swift-related commands
if echo "$COMMAND" | grep -qE "(^|&&|;|\|)\s*(swift|swiftc|xcodebuild|xcrun|xcode-select|xctest)\b"; then
    if ! command -v swift &> /dev/null; then
        echo '{"decision": "block", "message": "Swift is not installed. Please install Xcode or Xcode Command Line Tools.\n\nRun: xcode-select --install"}'
        exit 0
    fi
fi

# Allow the action to proceed
echo '{"decision": "allow"}'
