#!/usr/bin/env python3
"""Fetch Phosphor icons on demand from the unpkg CDN.

Usage:
    python3 fetch_icons.py arrow-right check-circle warning
    python3 fetch_icons.py --all

Icons are saved to assets/icons/phosphor/{name}.svg relative to the
pdf-factory skill directory. Already-downloaded icons are skipped.

Uses only Python stdlib — no additional dependencies required.
"""

import os
import sys
import urllib.request
import urllib.error

CDN_BASE = "https://unpkg.com/@phosphor-icons/core@2.1.1/assets/regular"
CDN_INDEX = "https://unpkg.com/@phosphor-icons/core@2.1.1/assets/regular/"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
ICONS_DIR = os.path.join(SKILL_DIR, "assets", "icons", "phosphor")


def fetch_icon(name: str) -> str:
    """Download a single icon SVG. Returns status string."""
    dest = os.path.join(ICONS_DIR, f"{name}.svg")
    if os.path.exists(dest):
        return f"  {name}.svg — already exists"

    url = f"{CDN_BASE}/{name}.svg"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "fetch_icons/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
    except urllib.error.HTTPError as exc:
        return f"  {name}.svg — failed ({exc.code} {exc.reason})"
    except urllib.error.URLError as exc:
        return f"  {name}.svg — failed ({exc.reason})"

    os.makedirs(ICONS_DIR, exist_ok=True)
    with open(dest, "wb") as f:
        f.write(data)
    return f"  {name}.svg — downloaded"


def fetch_all_names() -> list[str]:
    """Scrape the CDN directory listing for all .svg filenames."""
    try:
        req = urllib.request.Request(CDN_INDEX, headers={"User-Agent": "fetch_icons/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"Error fetching icon index: {exc}", file=sys.stderr)
        sys.exit(1)

    import re
    return sorted(set(
        m.group(1) for m in re.finditer(r'href="([^"]+)\.svg"', html)
    ))


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 fetch_icons.py <icon-name> [icon-name ...]\n"
              "       python3 fetch_icons.py --all", file=sys.stderr)
        sys.exit(1)

    if sys.argv[1] == "--all":
        print("Fetching icon index from CDN...")
        names = fetch_all_names()
        print(f"Found {len(names)} icons.")
    else:
        names = sys.argv[1:]

    for name in names:
        print(fetch_icon(name))

    print(f"\nDone. Icons stored in {ICONS_DIR}")


if __name__ == "__main__":
    main()
