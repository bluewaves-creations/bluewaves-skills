#!/usr/bin/env bash
#
# Build standalone .skill files (ZIP archives) for Claude.ai users.
# Each .skill file contains a single skill folder with its SKILL.md file.
#
# Usage:
#   ./scripts/build-skill-zips.sh                              # Build all skills
#   ./scripts/build-skill-zips.sh image-generator              # Build a single skill
#   ./scripts/build-skill-zips.sh --user bertrand               # All skills with user credentials
#   ./scripts/build-skill-zips.sh --user bertrand image-generator  # Single skill with credentials

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST_DIR="$REPO_ROOT/dist"
USER_NAME=""
FILTER=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --user)
            USER_NAME="$2"
            shift 2
            ;;
        *)
            FILTER="$1"
            shift
            ;;
    esac
done

# If --user is set, validate keys.json exists and user entry is present
if [[ -n "$USER_NAME" ]]; then
    KEYS_FILE="$REPO_ROOT/keys.json"
    if [[ ! -f "$KEYS_FILE" ]]; then
        echo "Error: keys.json not found. Copy keys.example.json to keys.json and fill in your keys." >&2
        exit 1
    fi
    # Verify the user exists in keys.json
    if ! python3 -c "import json,sys; d=json.load(open(sys.argv[1])); assert sys.argv[2] in d" "$KEYS_FILE" "$USER_NAME" 2>/dev/null; then
        echo "Error: User '$USER_NAME' not found in keys.json" >&2
        exit 1
    fi
fi

rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

count=0
total_size=0

for skill_dir in "$REPO_ROOT"/plugins/*/skills/*/; do
    skill_name="$(basename "$skill_dir")"

    # If a filter is provided, skip non-matching skills
    if [[ -n "$FILTER" && "$skill_name" != "$FILTER" ]]; then
        continue
    fi

    skill_md="$skill_dir/SKILL.md"
    if [[ ! -f "$skill_md" ]]; then
        echo "Warning: No SKILL.md in $skill_dir, skipping"
        continue
    fi

    # Determine which plugin this skill belongs to
    plugin_name="$(basename "$(dirname "$(dirname "$skill_dir")")")"

    # Create a temp directory with the correct structure: skill-name/SKILL.md
    tmp_dir="$(mktemp -d)"
    mkdir -p "$tmp_dir/$skill_name"
    cp "$skill_md" "$tmp_dir/$skill_name/SKILL.md"

    # Copy optional resource directories if present
    for resource_dir in scripts references assets; do
        if [[ -d "$skill_dir/$resource_dir" ]]; then
            cp -rL "$skill_dir/$resource_dir" "$tmp_dir/$skill_name/$resource_dir"
        fi
    done

    # Remove files that must never ship in ZIPs
    find "$tmp_dir" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$tmp_dir" \( -name "*.pyc" -o -name "*.pyo" -o -name ".DS_Store" -o -name "credentials.example.json" \) -delete 2>/dev/null || true

    # Handle credentials.json: inject per-user keys or strip
    if [[ -n "$USER_NAME" && -d "$tmp_dir/$skill_name/scripts" ]]; then
        # Inject user-specific credentials based on plugin type
        creds_file="$tmp_dir/$skill_name/scripts/credentials.json"
        case "$plugin_name" in
            media-factory)
                if [[ "$skill_name" == "podcast-generator" ]]; then
                    python3 -c "
import json, sys
keys = json.load(open(sys.argv[1]))
user = keys[sys.argv[2]]
creds = {'gemini_api_key': user['gemini_api_key']}
gw_name = user.get('ai_gateway_name', '')
if gw_name:
    acct = user['cloudflare_account_id']
    creds['gateway_url'] = f'https://gateway.ai.cloudflare.com/v1/{acct}/{gw_name}/google-ai-studio'
    token = user.get('cloudflare_api_token', '')
    if token:
        creds['gateway_token'] = token
json.dump(creds, open(sys.argv[3], 'w'), indent=2)
" "$KEYS_FILE" "$USER_NAME" "$creds_file"
                else
                    python3 -c "
import json, sys
keys = json.load(open(sys.argv[1]))
user = keys[sys.argv[2]]
json.dump({'api_key': user['fal_key']}, open(sys.argv[3], 'w'), indent=2)
" "$KEYS_FILE" "$USER_NAME" "$creds_file"
                fi
                ;;
            web-factory)
                python3 -c "
import json, sys
keys = json.load(open(sys.argv[1]))
user = keys[sys.argv[2]]
json.dump({
    'gateway_domain': user['gateway_domain'],
    'admin_token': user['web_factory_admin_token'],
    'api_token': user['cloudflare_api_token'],
    'account_id': user['cloudflare_account_id']
}, open(sys.argv[3], 'w'), indent=2)
" "$KEYS_FILE" "$USER_NAME" "$creds_file"
                ;;
            *)
                # Other plugins: remove credentials.json as usual
                find "$tmp_dir" -name "credentials.json" -delete 2>/dev/null || true
                ;;
        esac
    else
        # No --user: strip all credentials.json
        find "$tmp_dir" -name "credentials.json" -delete 2>/dev/null || true
    fi

    # Create the ZIP from inside the temp dir so the path is skill-name/SKILL.md
    (cd "$tmp_dir" && zip -q -r "$DIST_DIR/$skill_name.skill" "$skill_name")

    rm -rf "$tmp_dir"

    size=$(stat -f%z "$DIST_DIR/$skill_name.skill" 2>/dev/null || stat -c%s "$DIST_DIR/$skill_name.skill" 2>/dev/null)
    total_size=$((total_size + size))
    count=$((count + 1))

    size_kb="$((size / 1024)).$((size % 1024 * 10 / 1024))"
    printf "  %-40s %s KB\n" "$skill_name.skill" "$size_kb"
done

echo ""
total_kb="$((total_size / 1024)).$((total_size % 1024 * 10 / 1024))"
if [[ -n "$USER_NAME" ]]; then
    echo "$count .skill file(s) generated in dist/ for user '$USER_NAME' (total: ${total_kb} KB)"
else
    echo "$count .skill file(s) generated in dist/ (total: ${total_kb} KB)"
fi

if [[ -n "$FILTER" && $count -eq 0 ]]; then
    echo "Error: No skill found matching '$FILTER'" >&2
    exit 1
fi
