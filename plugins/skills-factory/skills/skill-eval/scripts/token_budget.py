#!/usr/bin/env python3
"""Token footprint analyzer for skills.

Reports context cost at three levels:
  Level 1 (metadata): tokens in name + description
  Level 2 (SKILL.md body): tokens per section
  Level 3 (references): tokens per reference file

Usage:
    token_budget.py --skill-path <dir>
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import count_tokens, parse_skill_md


# Thresholds for recommendations (calibrated for words * 0.75 heuristic)
DESCRIPTION_WARN = 800  # chars
BODY_WARN = 3000  # tokens
SECTION_WARN = 800  # tokens per section
REFERENCE_WARN = 2500  # tokens per reference file
TOTAL_WARN = 6000  # total tokens (body + refs)


def analyze_sections(content: str) -> list:
    """Break SKILL.md body into sections and count tokens per section."""
    # Strip frontmatter
    match = re.match(r"^---\n.*?\n---\n", content, re.DOTALL)
    body = content[match.end():] if match else content

    sections = []
    current_heading = "(intro)"
    current_lines = []

    for line in body.split("\n"):
        if re.match(r"^#{1,3}\s+", line):
            if current_lines:
                text = "\n".join(current_lines)
                sections.append((current_heading, count_tokens(text), len(current_lines)))
            current_heading = line.strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        text = "\n".join(current_lines)
        sections.append((current_heading, count_tokens(text), len(current_lines)))

    return sections


def analyze_references(skill_path: Path) -> list:
    """Analyze reference files and their token costs."""
    refs_dir = skill_path / "references"
    if not refs_dir.exists():
        return []

    refs = []
    for f in sorted(refs_dir.rglob("*")):
        if f.is_file() and f.suffix in (".md", ".txt", ".yaml", ".yml", ".json"):
            content = f.read_text(errors="replace")
            tokens = count_tokens(content)
            rel_path = str(f.relative_to(skill_path))
            refs.append((rel_path, tokens, len(content.splitlines())))

    return refs


def report(skill_path: Path) -> int:
    """Generate and print the token budget report."""
    skill_path = Path(skill_path).resolve()
    name, description, content = parse_skill_md(skill_path)

    print(f"Token Budget Analysis: {name}")
    print(f"{'=' * 60}")

    # Level 1: Metadata
    meta_tokens = count_tokens(f"{name} {description}")
    desc_chars = len(description)
    print(f"\nLevel 1 — Metadata (always in context)")
    print(f"  Name:        {name} ({count_tokens(name)} tokens)")
    print(f"  Description: {desc_chars} chars, ~{count_tokens(description)} tokens")
    if desc_chars > DESCRIPTION_WARN:
        print(f"  WARNING: Description is long ({desc_chars} chars). Consider tightening.")
    print(f"  Total:       ~{meta_tokens} tokens")

    # Level 2: SKILL.md body
    sections = analyze_sections(content)
    body_tokens = sum(t for _, t, _ in sections)
    body_lines = sum(l for _, _, l in sections)

    print(f"\nLevel 2 — SKILL.md body (loaded on trigger)")
    print(f"  Total: ~{body_tokens} tokens ({body_lines} lines)")
    if body_tokens > BODY_WARN:
        print(f"  WARNING: Body exceeds {BODY_WARN} tokens. Consider extracting to references.")

    print(f"\n  {'Section':<40} {'Tokens':>8} {'Lines':>8}")
    print(f"  {'-' * 40} {'-' * 8} {'-' * 8}")
    for heading, tokens, lines in sections:
        flag = " <-- heavy" if tokens > SECTION_WARN else ""
        display = heading[:38] + ".." if len(heading) > 40 else heading
        print(f"  {display:<40} {tokens:>8} {lines:>8}{flag}")

    # Level 3: References
    refs = analyze_references(skill_path)
    refs_tokens = sum(t for _, t, _ in refs)

    if refs:
        print(f"\nLevel 3 — References (loaded as needed)")
        print(f"  Total: ~{refs_tokens} tokens across {len(refs)} files")

        print(f"\n  {'File':<40} {'Tokens':>8} {'Lines':>8}")
        print(f"  {'-' * 40} {'-' * 8} {'-' * 8}")
        for path, tokens, lines in refs:
            flag = " <-- heavy" if tokens > REFERENCE_WARN else ""
            display = path[:38] + ".." if len(path) > 40 else path
            print(f"  {display:<40} {tokens:>8} {lines:>8}{flag}")

    # Summary
    total = body_tokens + refs_tokens
    print(f"\n{'=' * 60}")
    print(f"Summary:")
    print(f"  Metadata (always loaded):     ~{meta_tokens} tokens")
    print(f"  Body (on trigger):            ~{body_tokens} tokens")
    print(f"  References (on demand):       ~{refs_tokens} tokens")
    print(f"  Worst-case total:             ~{meta_tokens + total} tokens")
    print(f"  Typical-case (body only):     ~{meta_tokens + body_tokens} tokens")

    if total > TOTAL_WARN:
        print(f"\n  WARNING: Combined body + references ({total} tokens) is heavy.")

    # Recommendations
    recommendations = []
    heavy_sections = [(h, t) for h, t, _ in sections if t > SECTION_WARN]
    if heavy_sections:
        for heading, tokens in heavy_sections:
            recommendations.append(
                f"Extract '{heading}' ({tokens} tokens) to a reference file"
            )

    heavy_refs = [(p, t) for p, t, _ in refs if t > REFERENCE_WARN]
    if heavy_refs:
        for path, tokens in heavy_refs:
            recommendations.append(
                f"Consider splitting '{path}' ({tokens} tokens) or adding grep patterns"
            )

    if body_lines > 500:
        recommendations.append(
            f"SKILL.md body is {body_lines} lines (target: <500). Extract content to references."
        )

    if recommendations:
        print(f"\nRecommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")

    return 0


def main():
    parser = argparse.ArgumentParser(description="Token footprint analyzer for skills")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    args = parser.parse_args()

    return report(args.skill_path)


if __name__ == "__main__":
    sys.exit(main())
