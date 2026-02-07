#!/usr/bin/env python3
"""
Athena Package Validator - Validates .athena packages against the import specification

Usage:
    python validate_athena_package.py <path>

    <path> can be a .athena ZIP file or a staging directory.

Validates:
    - manifest.json exists and is valid JSON
    - version == 1, format == "athena"
    - notes array is non-empty
    - Every manifest file exists on disk
    - Every disk file appears in manifest
    - Aurora tags are valid (8 allowed values)
    - Cross-reference targets exist
    - Note header format (# title, > description, ---)

Exit codes:
    0 = valid (may have warnings)
    1 = errors found
"""

import json
import os
import re
import sys
import tempfile
import zipfile
from pathlib import Path

VALID_AURORA = {"commitments", "focus", "ops", "collab", "life", "explore", "archive", "library"}

HEADER_PATTERN = re.compile(
    r"^# .+\n\n> .+\n\n---\n",
    re.MULTILINE,
)

FRONTMATTER_PATTERN = re.compile(
    r"^---\n(.+?\n)---\n",
    re.DOTALL,
)

NOTE_LINK_PATTERN = re.compile(r"\[([^\]]*)\]\((notes/[^)]+)\)")
ASSET_LINK_PATTERN = re.compile(r"!\[([^\]]*)\]\((assets/[^)]+)\)")


def validate(path):
    """
    Validate an .athena package.

    Args:
        path: Path to a .athena ZIP file or staging directory.

    Returns:
        Tuple of (valid: bool, errors: list[str], warnings: list[str])
    """
    errors = []
    warnings = []
    work_dir = None
    cleanup = False

    path = Path(path).resolve()

    # Handle ZIP files
    if path.is_file() and (path.suffix == ".athena" or zipfile.is_zipfile(str(path))):
        work_dir = Path(tempfile.mkdtemp(prefix="athena-validate-"))
        cleanup = True
        try:
            with zipfile.ZipFile(str(path), "r") as zf:
                zf.extractall(str(work_dir))
        except zipfile.BadZipFile:
            return False, ["File is not a valid ZIP archive"], []
    elif path.is_dir():
        work_dir = path
    else:
        return False, [f"Path does not exist or is not a directory/ZIP: {path}"], []

    try:
        result = _validate_dir(work_dir, errors, warnings)
    finally:
        if cleanup and work_dir and work_dir.exists():
            import shutil
            shutil.rmtree(str(work_dir), ignore_errors=True)

    return len(errors) == 0, errors, warnings


def _validate_dir(work_dir, errors, warnings):
    """Validate the contents of an extracted package directory."""

    # Check manifest.json exists
    manifest_path = work_dir / "manifest.json"
    if not manifest_path.exists():
        errors.append("manifest.json not found in package root")
        return

    # Parse manifest
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"manifest.json is not valid JSON: {e}")
        return

    # Check required top-level fields
    if manifest.get("version") != 1:
        errors.append(f"manifest.json: 'version' must be 1, got {manifest.get('version')!r}")

    if manifest.get("format") != "athena":
        errors.append(f"manifest.json: 'format' must be 'athena', got {manifest.get('format')!r}")

    notes = manifest.get("notes")
    if not isinstance(notes, list) or len(notes) == 0:
        errors.append("manifest.json: 'notes' must be a non-empty array")
        return

    # Collect manifest-declared files
    manifest_note_files = set()
    manifest_asset_files = set()

    for i, note in enumerate(notes):
        prefix = f"manifest.json: notes[{i}]"

        # Required fields
        file_path = note.get("file")
        if not file_path:
            errors.append(f"{prefix}: missing required 'file' field")
        else:
            manifest_note_files.add(file_path)

        title = note.get("title")
        if not title:
            errors.append(f"{prefix}: missing required 'title' field")

        aurora = note.get("aurora")
        if not aurora:
            errors.append(f"{prefix}: missing required 'aurora' field")
        elif aurora not in VALID_AURORA:
            errors.append(
                f"{prefix}: invalid aurora tag '{aurora}' "
                f"-- must be one of: {', '.join(sorted(VALID_AURORA))}"
            )

        # Check note file exists on disk
        if file_path:
            note_full = work_dir / file_path
            if not note_full.exists():
                errors.append(f"Note file '{file_path}' declared in manifest but not found on disk")

        # Check assets
        assets = note.get("assets")
        if assets and isinstance(assets, list):
            for j, asset in enumerate(assets):
                asset_file = asset.get("file")
                if asset_file:
                    manifest_asset_files.add(asset_file)
                    asset_full = work_dir / asset_file
                    if not asset_full.exists():
                        errors.append(
                            f"Asset '{asset_file}' declared in manifest notes[{i}].assets[{j}] "
                            f"but not found on disk"
                        )

    # Check for disk files not in manifest
    notes_dir = work_dir / "notes"
    if notes_dir.exists() and notes_dir.is_dir():
        for md_file in notes_dir.glob("*.md"):
            rel = f"notes/{md_file.name}"
            if rel not in manifest_note_files:
                warnings.append(f"Disk file '{rel}' exists but is not listed in manifest")

    assets_dir = work_dir / "assets"
    if assets_dir.exists() and assets_dir.is_dir():
        for asset_file in assets_dir.iterdir():
            if asset_file.is_file():
                rel = f"assets/{asset_file.name}"
                if rel not in manifest_asset_files:
                    warnings.append(f"Disk file '{rel}' exists but is not referenced in manifest")

    # Validate note content
    all_note_files = manifest_note_files.copy()
    all_asset_files = manifest_asset_files.copy()

    # Also collect actual disk files for cross-reference validation
    disk_note_files = set()
    if notes_dir.exists():
        for f in notes_dir.glob("*.md"):
            disk_note_files.add(f"notes/{f.name}")

    disk_asset_files = set()
    if assets_dir.exists():
        for f in assets_dir.iterdir():
            if f.is_file():
                disk_asset_files.add(f"assets/{f.name}")

    existing_files = disk_note_files | disk_asset_files

    for note_file in manifest_note_files:
        note_path = work_dir / note_file
        if not note_path.exists():
            continue

        try:
            content = note_path.read_text(encoding="utf-8")
        except Exception as e:
            warnings.append(f"Could not read '{note_file}': {e}")
            continue

        # Strip YAML frontmatter if present
        body = content
        fm_match = FRONTMATTER_PATTERN.match(content)
        if fm_match:
            body = content[fm_match.end():]

            # Validate frontmatter aurora if present
            fm_text = fm_match.group(1)
            aurora_match = re.search(r"^aurora:\s*(\S+)", fm_text, re.MULTILINE)
            if aurora_match:
                fm_aurora = aurora_match.group(1).strip()
                if fm_aurora not in VALID_AURORA:
                    errors.append(
                        f"Note '{note_file}': frontmatter aurora tag '{fm_aurora}' is invalid "
                        f"-- must be one of: {', '.join(sorted(VALID_AURORA))}"
                    )

        # Validate header format
        body_stripped = body.lstrip("\n")
        if not HEADER_PATTERN.match(body_stripped):
            errors.append(
                f"Note '{note_file}': missing mandatory header format. "
                f"Must start with '# title\\n\\n> description\\n\\n---'"
            )

        # Validate cross-references
        for match in NOTE_LINK_PATTERN.finditer(content):
            target = match.group(2)
            if target not in existing_files:
                warnings.append(
                    f"Note '{note_file}': cross-reference target '{target}' not found in package"
                )

        for match in ASSET_LINK_PATTERN.finditer(content):
            target = match.group(2)
            if target not in existing_files:
                warnings.append(
                    f"Note '{note_file}': asset reference '{target}' not found in package"
                )


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_athena_package.py <path>")
        print()
        print("  <path>  Path to a .athena ZIP file or staging directory")
        print()
        print("Exit codes: 0 = valid, 1 = errors found")
        sys.exit(1)

    target = sys.argv[1]
    print(f"Validating: {target}")
    print()

    valid, errors, warnings = validate(target)

    # Print results
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  - {w}")
        print()

    if errors:
        print("Errors:")
        for e in errors:
            print(f"  - {e}")
        print()
        print(f"FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        sys.exit(1)
    else:
        print(f"PASSED: 0 errors, {len(warnings)} warning(s)")
        sys.exit(0)


if __name__ == "__main__":
    main()
