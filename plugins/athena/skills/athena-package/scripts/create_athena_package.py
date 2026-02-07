#!/usr/bin/env python3
"""
Athena Package Creator - Creates .athena import packages from a staging directory

Usage:
    python create_athena_package.py <staging-dir> [output-path]

    <staging-dir>   Directory containing manifest.json, notes/, and optionally assets/
    [output-path]   Optional output path for the .athena file (defaults to <dir-name>.athena in cwd)

The staging directory must pass validation before a package is created.
"""

import os
import sys
import zipfile
from pathlib import Path

# Import validate from the sibling module
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))
from validate_athena_package import validate


def create_package(staging_dir, output_path=None):
    """
    Create an .athena package from a staging directory.

    Args:
        staging_dir: Path to the staging directory
        output_path: Optional output path for the .athena file

    Returns:
        Path to the created .athena file, or None if error
    """
    staging_dir = Path(staging_dir).resolve()

    if not staging_dir.exists():
        print(f"Error: Staging directory not found: {staging_dir}")
        return None

    if not staging_dir.is_dir():
        print(f"Error: Path is not a directory: {staging_dir}")
        return None

    # Pre-flight validation
    print("Validating package...")
    valid, errors, warnings = validate(staging_dir)

    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  - {w}")

    if not valid:
        print("\nErrors:")
        for e in errors:
            print(f"  - {e}")
        print("\nValidation failed. Fix errors before creating package.")
        return None

    print("Validation passed.\n")

    # Determine output path
    if output_path:
        out = Path(output_path).resolve()
        if out.is_dir():
            out = out / f"{staging_dir.name}.athena"
    else:
        out = Path.cwd() / f"{staging_dir.name}.athena"

    # Ensure parent directory exists
    out.parent.mkdir(parents=True, exist_ok=True)

    # Collect files to package
    files_to_add = []

    # manifest.json
    manifest = staging_dir / "manifest.json"
    if manifest.exists():
        files_to_add.append(("manifest.json", manifest))

    # notes/
    notes_dir = staging_dir / "notes"
    if notes_dir.exists():
        for f in sorted(notes_dir.rglob("*")):
            if f.is_file():
                rel = f.relative_to(staging_dir)
                files_to_add.append((str(rel), f))

    # assets/
    assets_dir = staging_dir / "assets"
    if assets_dir.exists():
        for f in sorted(assets_dir.rglob("*")):
            if f.is_file():
                rel = f.relative_to(staging_dir)
                files_to_add.append((str(rel), f))

    if not files_to_add:
        print("Error: No files found to package")
        return None

    # Create ZIP
    try:
        total_size = 0
        with zipfile.ZipFile(str(out), "w", zipfile.ZIP_DEFLATED) as zf:
            for arcname, filepath in files_to_add:
                zf.write(str(filepath), arcname)
                total_size += filepath.stat().st_size
                print(f"  Added: {arcname}")

        zip_size = out.stat().st_size
        print(f"\nPackage created: {out}")
        print(f"  Files: {len(files_to_add)}")
        print(f"  Uncompressed: {_format_size(total_size)}")
        print(f"  Compressed: {_format_size(zip_size)}")
        return out

    except Exception as e:
        print(f"Error creating package: {e}")
        return None


def _format_size(size_bytes):
    """Format bytes into human-readable size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def main():
    if len(sys.argv) < 2:
        print("Usage: python create_athena_package.py <staging-dir> [output-path]")
        print()
        print("  <staging-dir>   Directory with manifest.json, notes/, and optionally assets/")
        print("  [output-path]   Optional output .athena file path (default: <dir-name>.athena)")
        sys.exit(1)

    staging_dir = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Creating package from: {staging_dir}")
    if output_path:
        print(f"Output: {output_path}")
    print()

    result = create_package(staging_dir, output_path)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
