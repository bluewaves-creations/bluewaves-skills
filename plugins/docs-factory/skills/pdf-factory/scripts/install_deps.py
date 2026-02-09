#!/usr/bin/env python3
"""Install pdf-factory dependencies."""
import subprocess
import sys

PACKAGES = [
    "xhtml2pdf",
    "reportlab",
    "pypdf",
    "pyhanko",
    "markdown",
    "lxml",
    "pillow",
    "html5lib",
    "cssselect2",
    "python-bidi",
    "arabic-reshaper",
]

def main():
    failed = []
    for pkg in PACKAGES:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--break-system-packages", pkg],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            print(f"  ✓ {pkg}")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ {pkg}: {e.stderr.decode().strip().splitlines()[-1] if e.stderr else 'unknown error'}")
            failed.append(pkg)

    print(f"\nInstalled {len(PACKAGES) - len(failed)}/{len(PACKAGES)} packages.")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        print("Try installing failed packages manually with:")
        for pkg in failed:
            print(f"  pip install --break-system-packages {pkg}")
        sys.exit(1)

if __name__ == "__main__":
    main()
