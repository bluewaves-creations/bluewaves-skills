#!/usr/bin/env python3
"""Automated script extraction from transcripts.

Parses transcript files for fenced code blocks, clusters similar blocks
by structural similarity, and generates parameterized candidate scripts.

Usage:
    extract_scripts.py --transcripts <glob> --output-dir <dir>
"""

import argparse
import glob as glob_mod
import hashlib
import re
import sys
from collections import defaultdict
from pathlib import Path


def extract_code_blocks(transcript: str) -> list:
    """Extract fenced code blocks from a transcript with language identifiers."""
    pattern = r"```(\w+)\n(.*?)```"
    blocks = []
    for match in re.finditer(pattern, transcript, re.DOTALL):
        lang = match.group(1).lower()
        code = match.group(2).strip()
        if lang in ("python", "py", "bash", "sh", "javascript", "js", "typescript", "ts"):
            blocks.append({"language": lang, "code": code, "length": len(code.splitlines())})
    return blocks


def structural_fingerprint(code: str) -> str:
    """Generate a structural fingerprint for code similarity comparison.

    Normalizes variable names and string literals to focus on structure:
    imports, function signatures, library calls.
    """
    # Normalize string literals
    normalized = re.sub(r'"[^"]*"', '"STR"', code)
    normalized = re.sub(r"'[^']*'", "'STR'", normalized)

    # Normalize variable names (rough)
    normalized = re.sub(r"\b[a-z_][a-z0-9_]{0,20}\b", "VAR", normalized)

    # Keep imports, function defs, and method calls
    key_lines = []
    for line in normalized.splitlines():
        stripped = line.strip()
        if any(stripped.startswith(kw) for kw in ("import ", "from ", "def ", "class ", "function ")):
            key_lines.append(stripped)
        elif re.search(r"\.\w+\(", stripped):  # method call
            key_lines.append(stripped)

    fingerprint = "\n".join(key_lines)
    return hashlib.md5(fingerprint.encode()).hexdigest()[:8]


def cluster_blocks(blocks: list, threshold: float = 0.5) -> list:
    """Cluster code blocks by structural fingerprint."""
    clusters = defaultdict(list)

    for block in blocks:
        fp = structural_fingerprint(block["code"])
        clusters[fp].append(block)

    # Sort clusters by frequency and total length
    scored = []
    for fp, members in clusters.items():
        frequency = len(members)
        total_length = sum(m["length"] for m in members)
        avg_length = total_length / frequency
        score = frequency * avg_length  # Prefer frequent, non-trivial blocks

        if frequency >= 2 and avg_length >= 5:  # At least 2 occurrences, 5+ lines
            scored.append({
                "fingerprint": fp,
                "members": members,
                "frequency": frequency,
                "avg_length": avg_length,
                "score": score,
                "language": members[0]["language"],
            })

    scored.sort(key=lambda c: c["score"], reverse=True)
    return scored


def generate_candidate_script(cluster: dict, index: int) -> str:
    """Generate a parameterized script from a cluster of similar code blocks."""
    lang = cluster["language"]
    representative = max(cluster["members"], key=lambda m: m["length"])
    code = representative["code"]

    if lang in ("python", "py"):
        header = f'''#!/usr/bin/env python3
"""
Auto-extracted script (cluster {index + 1})
Frequency: {cluster["frequency"]} occurrences across transcripts
Average length: {cluster["avg_length"]:.0f} lines

Review and parameterize before adding to skill scripts/.
"""

import argparse
import sys

'''
        # Try to wrap in a main function if not already
        if "def main" not in code:
            indented = "\n".join("    " + line for line in code.splitlines())
            code = f"def main():\n{indented}\n"

        footer = '''

if __name__ == "__main__":
    main()
'''
        return header + code + footer

    elif lang in ("bash", "sh"):
        header = f'''#!/usr/bin/env bash
# Auto-extracted script (cluster {index + 1})
# Frequency: {cluster["frequency"]} occurrences across transcripts
# Average length: {cluster["avg_length"]:.0f} lines
#
# Review and parameterize before adding to skill scripts/.

set -euo pipefail

'''
        return header + code + "\n"

    else:
        return f"// Auto-extracted ({lang}, cluster {index + 1})\n{code}\n"


def extract(transcripts_glob: str, output_dir: str) -> int:
    """Main extraction pipeline."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Collect all code blocks from transcripts
    all_blocks = []
    transcript_files = glob_mod.glob(transcripts_glob)

    if not transcript_files:
        print(f"No files matching: {transcripts_glob}")
        return 1

    for path in transcript_files:
        content = Path(path).read_text(errors="replace")
        blocks = extract_code_blocks(content)
        all_blocks.extend(blocks)

    print(f"Found {len(all_blocks)} code blocks across {len(transcript_files)} transcripts")

    if not all_blocks:
        print("No code blocks to extract.")
        return 0

    # Cluster similar blocks
    clusters = cluster_blocks(all_blocks)

    if not clusters:
        print("No repeated patterns found (need 2+ similar blocks with 5+ lines).")
        return 0

    print(f"Identified {len(clusters)} script candidates:")

    # Generate scripts
    for i, cluster in enumerate(clusters[:10]):  # Cap at 10
        lang_ext = {"python": "py", "py": "py", "bash": "sh", "sh": "sh",
                     "javascript": "js", "js": "js", "typescript": "ts", "ts": "ts"}
        ext = lang_ext.get(cluster["language"], "txt")
        filename = f"candidate_{i + 1}.{ext}"

        script = generate_candidate_script(cluster, i)
        (output_dir / filename).write_text(script)

        print(f"  {filename}: {cluster['frequency']}x occurrences, "
              f"~{cluster['avg_length']:.0f} lines, score={cluster['score']:.0f}")

    print(f"\nScripts written to {output_dir}/")
    print("Review, parameterize, and add useful scripts to your skill's scripts/ directory.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Extract repeated scripts from transcripts")
    parser.add_argument("--transcripts", required=True, help="Glob pattern for transcript files")
    parser.add_argument("--output-dir", required=True, help="Output directory for extracted scripts")
    args = parser.parse_args()

    return extract(args.transcripts, args.output_dir)


if __name__ == "__main__":
    sys.exit(main())
