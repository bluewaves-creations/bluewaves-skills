#!/usr/bin/env python3
"""Install pdf-factory dependencies."""
import shutil
import subprocess
import sys

PACKAGES = [
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

# svglib → rlpycairo → pycairo requires the cairo C library at build time.
# xhtml2pdf also depends on svglib, inheriting the same pycairo issue.
# Installing with --no-deps avoids pulling in pycairo; rlpycairo is a pure-Python
# fallback that works without the system library. Install these AFTER the normal
# packages so their real dependencies (reportlab, lxml, etc.) are already present.
NO_DEPS_PACKAGES = [
    "rlpycairo",
    "svglib",
    "xhtml2pdf",
]


def install_package(pkg, no_deps=False):
    """Install a single package, trying uv first, then pip --user, then pip --break-system-packages."""
    extra = ["--no-deps"] if no_deps else []
    uv = shutil.which("uv")
    if uv:
        result = subprocess.call(
            [uv, "pip", "install"] + extra + [pkg],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        if result == 0:
            return 0

    result = subprocess.call(
        [sys.executable, "-m", "pip", "install", "--user"] + extra + [pkg],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    if result == 0:
        return 0

    return subprocess.call(
        [sys.executable, "-m", "pip", "install", "--break-system-packages"] + extra + [pkg],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )


def main():
    all_packages = [(pkg, False) for pkg in PACKAGES] + [(pkg, True) for pkg in NO_DEPS_PACKAGES]
    failed = []
    for pkg, no_deps in all_packages:
        result = install_package(pkg, no_deps=no_deps)
        suffix = " (--no-deps)" if no_deps else ""
        if result == 0:
            print(f"  ✓ {pkg}{suffix}")
        else:
            print(f"  ✗ {pkg}{suffix}")
            failed.append(pkg)

    total = len(all_packages)
    print(f"\nInstalled {total - len(failed)}/{total} packages.")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        print("Try installing failed packages manually with:")
        for pkg in failed:
            print(f"  pip install {pkg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
