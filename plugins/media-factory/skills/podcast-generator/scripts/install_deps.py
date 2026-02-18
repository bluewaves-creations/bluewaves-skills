#!/usr/bin/env python3
"""Install Python dependencies required by the podcast-generator skill."""

import subprocess
import sys

DEPENDENCIES = ["google-genai", "pypdf"]


def main():
    print(f"Installing dependencies: {', '.join(DEPENDENCIES)}")
    try:
        subprocess.check_call(["uv", "pip", "install", "--quiet"] + DEPENDENCIES)
        print("All dependencies installed successfully.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--quiet"] + DEPENDENCIES
            )
            print("All dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error: pip install failed with exit code {e.returncode}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
