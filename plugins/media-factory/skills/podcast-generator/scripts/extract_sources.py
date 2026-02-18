#!/usr/bin/env python3
"""Extract text from source documents (.md and .pdf) in the sources/ directory."""

import argparse
import os
import sys


def extract_md(path):
    """Read markdown file and return its text content."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_pdf(path):
    """Extract text from a PDF file using pypdf."""
    try:
        from pypdf import PdfReader
    except ImportError:
        print(
            "Error: 'pypdf' is not installed. Run: uv pip install google-genai pypdf",
            file=sys.stderr,
        )
        sys.exit(1)

    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            pages.append(f"--- Page {i + 1} ---\n{text}")
    return "\n\n".join(pages)


EXTRACTORS = {
    ".md": extract_md,
    ".pdf": extract_pdf,
}


def extract_file(path):
    """Extract text from a single file based on its extension."""
    ext = os.path.splitext(path)[1].lower()
    extractor = EXTRACTORS.get(ext)
    if not extractor:
        print(f"Warning: Unsupported file type '{ext}' — skipping {path}", file=sys.stderr)
        return None
    return extractor(path)


def find_sources(directory):
    """Find all supported source files in a directory."""
    supported = set(EXTRACTORS.keys())
    files = []
    for name in sorted(os.listdir(directory)):
        ext = os.path.splitext(name)[1].lower()
        if ext in supported:
            files.append(os.path.join(directory, name))
    return files


def main():
    parser = argparse.ArgumentParser(
        description="Extract text from source documents (.md, .pdf)."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Path to a specific file or directory (default: sources/ in current directory)",
    )
    args = parser.parse_args()

    # Default to sources/ in the current working directory
    default_sources = os.path.join(os.getcwd(), "sources")

    target = args.path or default_sources

    if os.path.isfile(target):
        text = extract_file(target)
        if text:
            print(f"=== {os.path.basename(target)} ===\n")
            print(text)
        else:
            sys.exit(1)
    elif os.path.isdir(target):
        files = find_sources(target)
        if not files:
            print(f"Error: No supported files (.md, .pdf) found in {target}", file=sys.stderr)
            sys.exit(1)
        for i, path in enumerate(files):
            if i > 0:
                print("\n" + "=" * 60 + "\n")
            print(f"=== {os.path.basename(path)} ===\n")
            text = extract_file(path)
            if text:
                print(text)
    else:
        print(f"Error: Path not found: {target}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
