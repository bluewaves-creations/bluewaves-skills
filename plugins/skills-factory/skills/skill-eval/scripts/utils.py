#!/usr/bin/env python3
"""Shared utilities for skill-eval scripts."""

import re
from pathlib import Path


def parse_skill_md(skill_path: Path) -> tuple:
    """Parse a SKILL.md file, returning (name, description, full_content).

    Args:
        skill_path: Path to skill directory containing SKILL.md

    Returns:
        Tuple of (name, description, full_content)
    """
    content = (skill_path / "SKILL.md").read_text()
    lines = content.split("\n")

    if lines[0].strip() != "---":
        raise ValueError("SKILL.md missing frontmatter (no opening ---)")

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        raise ValueError("SKILL.md missing frontmatter (no closing ---)")

    name = ""
    description = ""
    frontmatter_lines = lines[1:end_idx]
    i = 0
    while i < len(frontmatter_lines):
        line = frontmatter_lines[i]
        if line.startswith("name:"):
            name = line[len("name:"):].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            value = line[len("description:"):].strip()
            if value in (">", "|", ">-", "|-"):
                continuation_lines = []
                i += 1
                while i < len(frontmatter_lines) and (
                    frontmatter_lines[i].startswith("  ")
                    or frontmatter_lines[i].startswith("\t")
                ):
                    continuation_lines.append(frontmatter_lines[i].strip())
                    i += 1
                description = " ".join(continuation_lines)
                continue
            else:
                description = value.strip('"').strip("'")
        i += 1

    return name, description, content


def count_tokens(text: str) -> int:
    """Approximate token count using word-based heuristic.

    Uses words * 0.75 as a rough approximation of Claude tokenizer output
    for English text (~0.75 tokens per whitespace-delimited word).
    """
    words = len(text.split())
    return int(words * 0.75)


def find_skill_eval_dir(skill_path: Path) -> Path:
    """Locate or return the .skill-eval/ directory for a skill.

    Args:
        skill_path: Path to skill directory

    Returns:
        Path to .skill-eval/ directory (may not exist yet)
    """
    return skill_path / ".skill-eval"


def get_next_run_id(eval_dir: Path) -> str:
    """Get the next sequential run ID (e.g., '001', '002').

    Args:
        eval_dir: Path to .skill-eval/ directory

    Returns:
        Zero-padded 3-digit run ID string
    """
    runs_dir = eval_dir / "runs"
    if not runs_dir.exists():
        return "001"

    existing = sorted(
        [d.name for d in runs_dir.iterdir() if d.is_dir() and d.name.isdigit()]
    )
    if not existing:
        return "001"

    return f"{int(existing[-1]) + 1:03d}"


def hash_file(path: Path) -> str:
    """Compute a short hash of a file's contents."""
    import hashlib

    content = path.read_bytes()
    return hashlib.sha256(content).hexdigest()[:12]


def load_yaml(path: Path) -> dict:
    """Load a YAML file, trying PyYAML first, falling back to basic parsing."""
    text = path.read_text()
    try:
        import yaml

        return yaml.safe_load(text)
    except ImportError:
        return _basic_yaml_parse(text)


def _basic_yaml_parse(text: str) -> dict:
    """Minimal YAML-like parser for simple key-value files."""
    result = {}
    current_key = None
    current_list = None

    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("- ") and current_key:
            if current_list is None:
                current_list = []
                result[current_key] = current_list
            current_list.append(stripped[2:].strip().strip('"').strip("'"))
            continue

        if ":" in stripped:
            current_list = None
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            current_key = key
            if value:
                result[key] = value
            continue

    return result
