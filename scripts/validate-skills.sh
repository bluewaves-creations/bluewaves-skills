#!/usr/bin/env bash
#
# Validate skills using the skills-ref library.
# Runs skills-ref validate against every skill in the marketplace.
#
# Usage:
#   ./scripts/validate-skills.sh              # Validate all skills
#   ./scripts/validate-skills.sh skill-shaper # Validate one skill

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FILTER="${1:-}"

# Check if skills-ref is available
if ! command -v skills-ref &>/dev/null; then
    echo "skills-ref CLI not found. Attempting to install..."
    SUBMODULE_PATH="$REPO_ROOT/deps/agentskills/skills-ref"
    if [[ -d "$SUBMODULE_PATH" ]]; then
        uv pip install -e "$SUBMODULE_PATH"
    else
        echo "Error: skills-ref not installed and submodule not found at $SUBMODULE_PATH"
        echo ""
        echo "To set up:"
        echo "  git submodule update --init"
        echo "  uv pip install -e deps/agentskills/skills-ref/"
        exit 1
    fi
fi

passed=0
failed=0
errors=""

for skill_dir in "$REPO_ROOT"/plugins/*/skills/*/; do
    skill_name="$(basename "$skill_dir")"

    # If a filter is provided, skip non-matching skills
    if [[ -n "$FILTER" && "$skill_name" != "$FILTER" ]]; then
        continue
    fi

    # Check SKILL.md exists
    if [[ ! -f "$skill_dir/SKILL.md" ]]; then
        echo "  SKIP  $skill_name (no SKILL.md)"
        continue
    fi

    if skills-ref validate "$skill_dir" &>/dev/null; then
        printf "  %-8s %s\n" "PASS" "$skill_name"
        passed=$((passed + 1))
    else
        printf "  %-8s %s\n" "FAIL" "$skill_name"
        failed=$((failed + 1))
        errors="$errors\n--- $skill_name ---\n$(skills-ref validate "$skill_dir" 2>&1)"
    fi
done

echo ""
echo "Results: $passed passed, $failed failed"

if [[ -n "$FILTER" && $passed -eq 0 && $failed -eq 0 ]]; then
    echo "Error: No skill found matching '$FILTER'" >&2
    exit 1
fi

if [[ $failed -gt 0 ]]; then
    echo ""
    echo "Failures:"
    printf "%b\n" "$errors"
    exit 1
fi
