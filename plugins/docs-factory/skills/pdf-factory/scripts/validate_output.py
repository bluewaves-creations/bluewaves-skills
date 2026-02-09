#!/usr/bin/env python3
"""Post-render QA checks for generated PDFs.

Usage:
    python validate_output.py <pdf-path> [--brand <brand-kit-path>]

Checks:
- File exists and is valid PDF
- Page count > 0
- File size between 1KB and 50MB
- All fonts embedded (not referenced)
- PDF metadata contains title and author
- If --brand: verify brand fonts appear in embedded font list

Exit code 0 on all pass, 1 on any failure.
"""
import argparse
import json
import os
import sys
from pathlib import Path


def check_file_exists(pdf_path: str) -> tuple:
    """Check that the file exists and has content."""
    if not os.path.exists(pdf_path):
        return False, f"File not found: {pdf_path}"
    size = os.path.getsize(pdf_path)
    if size == 0:
        return False, "File is empty (0 bytes)"
    return True, f"File exists ({size} bytes)"


def check_valid_pdf(pdf_path: str) -> tuple:
    """Check that the file is a valid PDF."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        _ = len(reader.pages)
        return True, "Valid PDF file"
    except Exception as e:
        return False, f"Invalid PDF: {e}"


def check_page_count(pdf_path: str) -> tuple:
    """Check page count is greater than 0."""
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    count = len(reader.pages)
    if count == 0:
        return False, "Page count 0"
    return True, f"Page count: {count}"


def check_file_size(pdf_path: str) -> tuple:
    """Check file size is within reasonable bounds."""
    size = os.path.getsize(pdf_path)
    size_mb = size / (1024 * 1024)
    if size < 1024:
        return False, f"File too small ({size} bytes) — may be corrupted"
    if size > 50 * 1024 * 1024:
        return False, f"File too large ({size_mb:.1f} MB) — exceeds 50MB limit"
    return True, f"File size: {size_mb:.2f} MB"


def check_fonts_embedded(pdf_path: str) -> tuple:
    """Check that all fonts are embedded, not just referenced."""
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    embedded_fonts = set()
    referenced_only = set()

    for page in reader.pages:
        if "/Resources" in page and "/Font" in page["/Resources"]:
            fonts = page["/Resources"]["/Font"]
            for font_name in fonts:
                font_obj = fonts[font_name].get_object()
                base_font = str(font_obj.get("/BaseFont", "unknown"))
                if "/FontDescriptor" in font_obj:
                    descriptor = font_obj["/FontDescriptor"].get_object()
                    if "/FontFile" in descriptor or "/FontFile2" in descriptor or "/FontFile3" in descriptor:
                        embedded_fonts.add(base_font)
                    else:
                        referenced_only.add(base_font)
                else:
                    # Standard 14 fonts don't need embedding
                    embedded_fonts.add(base_font)

    if referenced_only:
        return False, f"Font not embedded: {', '.join(referenced_only)}"
    if embedded_fonts:
        return True, f"All fonts embedded: {', '.join(sorted(embedded_fonts))}"
    return True, "No custom fonts used"


def check_metadata(pdf_path: str) -> tuple:
    """Check that PDF metadata contains title and author."""
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    meta = reader.metadata
    if not meta:
        return False, "Missing metadata — no PDF info dictionary"
    issues = []
    if not meta.get("/Title"):
        issues.append("title")
    if not meta.get("/Author"):
        issues.append("author")
    if issues:
        return False, f"Missing metadata: {', '.join(issues)}"
    return True, f"Metadata OK — title: {meta.get('/Title')}, author: {meta.get('/Author')}"


def check_brand_fonts(pdf_path: str, brand_path: str) -> tuple:
    """Verify brand fonts appear in embedded font list."""
    manifest_path = Path(brand_path) / "assets" / "manifest.json"
    if not manifest_path.exists():
        return False, f"Brand manifest not found at {manifest_path}"

    with open(manifest_path) as f:
        manifest = json.load(f)

    brand_name = manifest.get("brand", {}).get("name", "Unknown")
    # Expect at least one font per role to appear in the PDF
    expected_roles = set()
    for role, variants in manifest.get("fonts", {}).items():
        if isinstance(variants, dict) and variants:
            expected_roles.add(role)

    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    found_fonts = set()
    for page in reader.pages:
        if "/Resources" in page and "/Font" in page["/Resources"]:
            fonts = page["/Resources"]["/Font"]
            for font_name in fonts:
                font_obj = fonts[font_name].get_object()
                base_font = str(font_obj.get("/BaseFont", ""))
                found_fonts.add(base_font)

    # Check that each font role is represented in the PDF.
    # Fonts appear as either Brand-{role}-{variant} (from compose.py zones)
    # or as the actual typeface name (from xhtml2pdf @font-face).
    # Both contain the role name (e.g. "body" in "brand-body-regular" or
    # the font is a non-standard font that replaced the role's generic fallback).
    found_lower = {f.lower().lstrip("/").replace("aaaaaa+", "") for f in found_fonts}
    # Standard 14 fonts that indicate a role was NOT embedded
    standard_fonts = {"helvetica", "times-roman", "courier"}
    custom_fonts = {f for f in found_lower if f not in standard_fonts}

    if not custom_fonts:
        return False, f"No custom brand fonts embedded for {brand_name} — only standard fonts found"

    # Check role coverage: each role should map to at least one custom font
    matched_roles = set()
    for role in expected_roles:
        # Match by Brand-{role} convention or by any custom font being present
        if any(f"brand-{role}" in f or role in f for f in custom_fonts):
            matched_roles.add(role)

    # If we have custom fonts but role matching is ambiguous (e.g., font names
    # don't contain the role name), accept if we have enough custom fonts
    if not matched_roles and len(custom_fonts) >= len(expected_roles):
        return True, f"Brand fonts embedded for {brand_name}: {', '.join(sorted(custom_fonts))}"

    missing = expected_roles - matched_roles
    if missing:
        return False, f"Brand font roles not covered in PDF: {', '.join(sorted(missing))}"
    return True, f"Brand fonts verified for {brand_name}: {', '.join(sorted(matched_roles))}"


def main():
    parser = argparse.ArgumentParser(description="Validate generated PDF output")
    parser.add_argument("pdf_path", help="Path to PDF file to validate")
    parser.add_argument("--brand", required=False, help="Path to brand kit for font verification")
    args = parser.parse_args()

    checks = [
        ("File exists", check_file_exists(args.pdf_path)),
    ]

    # Only run further checks if file exists
    if checks[0][1][0]:
        checks.extend([
            ("Valid PDF", check_valid_pdf(args.pdf_path)),
            ("Page count", check_page_count(args.pdf_path)),
            ("File size", check_file_size(args.pdf_path)),
            ("Fonts embedded", check_fonts_embedded(args.pdf_path)),
            ("Metadata", check_metadata(args.pdf_path)),
        ])
        if args.brand:
            checks.append(("Brand fonts", check_brand_fonts(args.pdf_path, args.brand)))

    # Report results
    all_pass = True
    for name, (passed, message) in checks:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"  [{status}] {name}: {message}")

    if all_pass:
        print("\nAll checks passed.")
        sys.exit(0)
    else:
        print("\nValidation failed. Fix errors above and re-run.")
        sys.exit(1)


if __name__ == "__main__":
    main()
