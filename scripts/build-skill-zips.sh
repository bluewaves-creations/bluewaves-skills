#!/usr/bin/env bash
#
# Build standalone .skill files (ZIP archives) for Claude.ai users.
# Each .skill file contains a single skill folder with its SKILL.md file.
#
# Usage:
#   ./scripts/build-skill-zips.sh                    # Build all skills
#   ./scripts/build-skill-zips.sh image-generator     # Build a single skill

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST_DIR="$REPO_ROOT/dist"
FILTER="${1:-}"

rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

count=0
total_size=0

# First pass: detect duplicate skill names across plugins
duplicate_names=""
for skill_dir in "$REPO_ROOT"/plugins/*/skills/*/; do
    [[ -f "$skill_dir/SKILL.md" ]] || continue
    sname="$(basename "$skill_dir")"
    duplicate_names="$duplicate_names $sname"
done
# Names appearing more than once are duplicates
dup_list=$(echo "$duplicate_names" | tr ' ' '\n' | sort | uniq -d | tr '\n' ' ')

for skill_dir in "$REPO_ROOT"/plugins/*/skills/*/; do
    skill_name="$(basename "$skill_dir")"
    plugin_name="$(basename "$(dirname "$(dirname "$skill_dir")")")"

    # If a filter is provided, skip non-matching skills
    if [[ -n "$FILTER" && "$skill_name" != "$FILTER" ]]; then
        continue
    fi

    skill_md="$skill_dir/SKILL.md"
    if [[ ! -f "$skill_md" ]]; then
        echo "Warning: No SKILL.md in $skill_dir, skipping"
        continue
    fi

    # Use prefixed name when multiple plugins have the same skill name
    if echo "$dup_list" | grep -qw "$skill_name"; then
        output_name="${plugin_name}-${skill_name}"
    else
        output_name="$skill_name"
    fi

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
    find "$tmp_dir" \( -name "*.pyc" -o -name "*.pyo" -o -name ".DS_Store" -o -name "credentials.example.json" -o -name "credentials.json" \) -delete 2>/dev/null || true

    # Create the ZIP from inside the temp dir so the path is skill-name/SKILL.md
    (cd "$tmp_dir" && zip -q -r "$DIST_DIR/$output_name.skill" "$skill_name")

    rm -rf "$tmp_dir"

    size=$(stat -f%z "$DIST_DIR/$output_name.skill" 2>/dev/null || stat -c%s "$DIST_DIR/$output_name.skill" 2>/dev/null)
    total_size=$((total_size + size))
    count=$((count + 1))

    size_kb="$((size / 1024)).$((size % 1024 * 10 / 1024))"
    printf "  %-40s %s KB\n" "$output_name.skill" "$size_kb"
done

echo ""
total_kb="$((total_size / 1024)).$((total_size % 1024 * 10 / 1024))"
echo "$count .skill file(s) generated in dist/ (total: ${total_kb} KB)"

if [[ -n "$FILTER" && $count -eq 0 ]]; then
    echo "Error: No skill found matching '$FILTER'" >&2
    exit 1
fi
