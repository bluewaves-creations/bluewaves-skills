#!/bin/bash
# Validate web-factory credentials before relevant commands.
#
# This hook runs before Bash tool use to ensure credentials are configured.
# It only validates when the command involves wrangler, site_api, or
# web-factory environment variables.
# Checks both credentials.json and environment variables.

# Gracefully allow if jq is not available
if ! command -v jq &> /dev/null; then
    echo '{"decision": "allow"}'
    exit 0
fi

# Read the tool input from stdin
INPUT=$(cat)

# Extract the command being run
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Only validate if the command involves web-factory operations
if echo "$COMMAND" | grep -qE "wrangler|site_api|CLOUDFLARE|WEB_FACTORY"; then
  # Check credentials file first
  SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)/scripts"
  CREDS_FILE="$SCRIPT_DIR/credentials.json"
  if [ -f "$CREDS_FILE" ]; then
    TOKEN=$(jq -r '.admin_token // empty' "$CREDS_FILE" 2>/dev/null)
    if [ -n "$TOKEN" ] && [ "$TOKEN" != "YOUR_ADMIN_TOKEN_HERE" ]; then
      echo '{"decision": "allow"}'
      exit 0
    fi
    # For wrangler commands, also check Cloudflare API token
    if echo "$COMMAND" | grep -qE "wrangler"; then
      CF_TOKEN=$(jq -r '.api_token // empty' "$CREDS_FILE" 2>/dev/null)
      if [ -n "$CF_TOKEN" ] && [ "$CF_TOKEN" != "YOUR_CLOUDFLARE_API_TOKEN_HERE" ]; then
        echo '{"decision": "allow"}'
        exit 0
      fi
    fi
  fi

  # Check env vars
  if [ -n "$WEB_FACTORY_ADMIN_TOKEN" ]; then
    echo '{"decision": "allow"}'
    exit 0
  fi
  if echo "$COMMAND" | grep -qE "wrangler" && [ -n "$CLOUDFLARE_API_TOKEN" ]; then
    echo '{"decision": "allow"}'
    exit 0
  fi

  # No credentials found
  echo '{"decision": "block", "message": "web-factory credentials not found. Place credentials.json in scripts/ directory or set WEB_FACTORY_ADMIN_TOKEN / CLOUDFLARE_API_TOKEN in ~/.zshrc. Run /web-factory:check-cf-key for help."}'
  exit 0
fi

# Allow the action to proceed
echo '{"decision": "allow"}'
